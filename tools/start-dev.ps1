param(
    [ValidateSet('with-nifi', 'without-nifi')]
    [string]$Profile = 'without-nifi',
    [ValidateSet('kafka1', 'kafka2', 'kafka3', 'spark-master', 'spark-worker1', 'spark-worker2', 'nifi')]
    [string]$ChildService,
    [switch]$CheckOnly,
    [string]$DockerCliPath = $env:DOCKER_CLI
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$sparkRoot = Join-Path (Split-Path -Parent $projectRoot) 'Oder-insight/Spark-exam/spark-4.1.3-bin-hadoop3-1'
$sparkClass = Join-Path $sparkRoot 'bin/spark-class.cmd'
$bundledJavaHome = Join-Path $projectRoot 'infra/runtime/temurin-jdk21/jdk-21.0.12.1+1'
$bundledJavaPath = Join-Path $bundledJavaHome 'bin/java.exe'
$machineRoot = Split-Path -Parent (Split-Path -Parent $projectRoot)
$nifiComposeRoot = Join-Path $machineRoot 'nifi-cluster/nifi-compose'
$nifiComposeFile = Join-Path $nifiComposeRoot 'compose_cluster.yaml'
$scriptPath = $PSCommandPath
$powershellPath = Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0/powershell.exe'
$servicePorts = [ordered]@{
    'kafka1' = @(9092, 9093, 29092)
    'kafka2' = @(9094, 9095, 29094)
    'kafka3' = @(9096, 9097, 29096)
    'spark-master' = @(7077, 8080)
    'spark-worker1' = @(7078, 8081)
    'spark-worker2' = @(7079, 8082)
    'nifi' = @(8443, 8444, 8445)
}

function Initialize-JavaRuntime {
    $candidates = New-Object System.Collections.Generic.List[string]
    $candidates.Add($bundledJavaPath)
    if (-not [string]::IsNullOrWhiteSpace($env:JAVA_HOME)) {
        $candidates.Add((Join-Path $env:JAVA_HOME 'bin/java.exe'))
    }
    $command = Get-Command java.exe -ErrorAction SilentlyContinue
    if ($null -ne $command) { $candidates.Add($command.Source) }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { continue }
        $resolvedJava = (Resolve-Path -LiteralPath $candidate).Path
        $javaBin = Split-Path -Parent $resolvedJava
        $env:JAVA_HOME = Split-Path -Parent $javaBin
        $pathEntries = @($env:Path -split ';')
        if ($javaBin -notin $pathEntries) { $env:Path = "$javaBin;$env:Path" }
        return $resolvedJava
    }

    throw "Java was not found. Expected the project runtime at: $bundledJavaPath"
}

function Test-Listening([int]$Port) {
    try {
        $listeners = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
        return @($listeners | Where-Object { $_.Port -eq $Port }).Count -gt 0
    } catch {
        return $false
    }
}

function Test-ServicePortInUse([string]$Name) {
    foreach ($port in $servicePorts[$Name]) {
        if (Test-Listening $port) {
            Write-Host "$Name port $port is in use; skipped. Verify the existing service."
            return $true
        }
    }
    return $false
}

function Resolve-DockerCli {
    $candidates = New-Object System.Collections.Generic.List[string]
    if (-not [string]::IsNullOrWhiteSpace($DockerCliPath)) {
        $candidates.Add($DockerCliPath.Trim('"'))
    }
    $command = Get-Command docker.exe -ErrorAction SilentlyContinue
    if ($null -ne $command) { $candidates.Add($command.Source) }
    foreach ($candidate in @(
        (Join-Path $env:ProgramFiles 'Docker/Docker/resources/bin/docker.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs/DockerDesktop/resources/bin/docker.exe'),
        (Join-Path $env:LOCALAPPDATA 'Docker/resources/bin/docker.exe'),
        (Join-Path $env:USERPROFILE '.docker/bin/docker.exe'),
        (Join-Path $env:ProgramData 'chocolatey/bin/docker.exe')
    )) {
        $candidates.Add($candidate)
    }
    foreach ($candidate in $candidates | Select-Object -Unique) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $null
}

function Invoke-Docker([string]$DockerCli, [string[]]$Arguments) {
    $previousErrorAction = $ErrorActionPreference
    try {
        # Windows PowerShell 5.1 wraps native stderr in ErrorRecord objects.
        $ErrorActionPreference = 'Continue'
        try {
            $output = & $DockerCli @Arguments 2>&1
            $exitCode = $LASTEXITCODE
        } catch {
            $output = @($_.Exception.Message)
            $exitCode = 1
        }
    } finally {
        $ErrorActionPreference = $previousErrorAction
    }
    return @{ ExitCode = $exitCode; Output = @($output) }
}

function Get-NifiPreflightIssues([string]$DockerCli) {
    $issues = New-Object System.Collections.Generic.List[string]
    if (-not (Test-Path -LiteralPath $nifiComposeFile -PathType Leaf)) {
        $issues.Add("NiFi Compose file is missing: $nifiComposeFile")
        return $issues
    }
    if ([string]::IsNullOrWhiteSpace($DockerCli)) {
        $issues.Add('docker.exe was not found. Install/start Docker Desktop or set DOCKER_CLI to docker.exe.')
        return $issues
    }
    $engine = Invoke-Docker $DockerCli @('version', '--format', '{{.Server.Version}}')
    if ($engine.ExitCode -ne 0) {
        $issues.Add('Docker Engine is not available. Start Docker Desktop and wait until it is ready.')
        return $issues
    }
    $compose = Invoke-Docker $DockerCli @('compose', 'version')
    if ($compose.ExitCode -ne 0) {
        $issues.Add('Docker Compose v2 is not available from the selected Docker CLI.')
        return $issues
    }
    $config = Invoke-Docker $DockerCli @(
        'compose', '--project-directory', $nifiComposeRoot,
        '-f', $nifiComposeFile, 'config', '--quiet'
    )
    if ($config.ExitCode -ne 0) {
        $issues.Add('NiFi Docker Compose configuration is invalid. Check compose_cluster.yaml and its .env values.')
        return $issues
    }
    $services = Invoke-Docker $DockerCli @(
        'compose', '--project-directory', $nifiComposeRoot,
        '-f', $nifiComposeFile, 'config', '--services'
    )
    $expected = @('initialize', 'zk1', 'zk2', 'zk3', 'nifi1', 'nifi2', 'nifi3')
    $actual = @($services.Output | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    foreach ($name in $expected) {
        if ($name -notin $actual) { $issues.Add("NiFi Compose service is missing: $name") }
    }
    return $issues
}

function Confirm-Files([bool]$IncludeNifi, [string]$JavaPath) {
    $required = @(
        $JavaPath,
        $sparkClass,
        (Join-Path $sparkRoot 'jars'),
        (Join-Path $PSScriptRoot 'kafka.ps1')
    )
    if ($IncludeNifi) { $required += $nifiComposeFile }
    foreach ($nodeNumber in 1..3) {
        $required += Join-Path $projectRoot "infra/kafka/node$nodeNumber.properties"
        $required += Join-Path $projectRoot "data/kafka/node$nodeNumber/meta.properties"
    }
    $required += Join-Path $projectRoot 'infra/runtime/kafka_2.13-4.1.2/libs'
    foreach ($path in $required) {
        if (-not (Test-Path -LiteralPath $path)) { throw "Required path missing: $path" }
    }
}

# One launcher/service owner per checkout. Repeated clicks cannot create duplicate children.
$launchTarget = if ([string]::IsNullOrWhiteSpace($ChildService)) { $Profile } else { $ChildService }
$hasher = [System.Security.Cryptography.SHA256]::Create()
try {
    $rootId = [BitConverter]::ToString($hasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($projectRoot.ToLowerInvariant()))).Replace('-', '').Substring(0, 16)
} finally { $hasher.Dispose() }
$mutex = New-Object System.Threading.Mutex($false, "Local\VillageDev-$rootId-$launchTarget")
$locked = $false
try {
    try { $locked = $mutex.WaitOne(0) } catch [System.Threading.AbandonedMutexException] { $locked = $true }
    if (-not $locked) { Write-Host "$launchTarget already has a launcher window. Skipped."; return }

    $javaPath = Initialize-JavaRuntime
    $includeNifi = if ([string]::IsNullOrWhiteSpace($ChildService)) {
        $Profile -eq 'with-nifi'
    } else {
        $ChildService -eq 'nifi'
    }
    Confirm-Files $includeNifi $javaPath
    $dockerCli = $null
    $nifiPreflightIssues = @()
    if ($includeNifi) {
        $dockerCli = Resolve-DockerCli
        $nifiPreflightIssues = @(Get-NifiPreflightIssues $dockerCli)
    }

    if ($CheckOnly) {
        Write-Host "Java: $javaPath"
        Write-Host "Spark: $sparkRoot"
        $checkedServices = if (-not [string]::IsNullOrWhiteSpace($ChildService)) {
            @($ChildService)
        } else {
            $profileServices = @('kafka1', 'kafka2', 'kafka3', 'spark-master', 'spark-worker1')
            if ($Profile -eq 'without-nifi') { $profileServices += 'spark-worker2' }
            if ($Profile -eq 'with-nifi') { $profileServices += 'nifi' }
            $profileServices
        }
        if ($includeNifi) { Write-Host "NiFi Compose: $nifiComposeFile" }
        foreach ($name in $checkedServices) {
            if (-not (Test-ServicePortInUse $name)) { Write-Host "$name ports are free." }
        }
        if (-not $includeNifi) {
            Write-Host "Docker/NiFi check skipped for $launchTarget."
        } elseif ($nifiPreflightIssues.Count -eq 0) {
            Write-Host "Docker CLI: $dockerCli"
            Write-Host 'NiFi Docker Compose preflight passed.'
        } else {
            Write-Warning 'NiFi Docker Compose preflight did not pass:'
            foreach ($issue in $nifiPreflightIssues) { Write-Warning "- $issue" }
        }
        if ($includeNifi) {
            Write-Host 'Kafka/Spark/NiFi files and service ports were checked. No services were started.'
        } else {
            Write-Host 'Kafka/Spark files and selected service ports were checked. No services were started.'
        }
        return
    }

    if ([string]::IsNullOrWhiteSpace($ChildService)) {
        $servicesToOpen = @('kafka1', 'kafka2', 'kafka3', 'spark-master', 'spark-worker1')
        if ($Profile -eq 'without-nifi') { $servicesToOpen += 'spark-worker2' }
        if ($Profile -eq 'with-nifi') { $servicesToOpen += 'nifi' }
        foreach ($name in $servicesToOpen) {
            if ($name -eq 'nifi' -and $nifiPreflightIssues.Count -gt 0) {
                Write-Warning 'nifi was skipped because the Docker Compose preflight did not pass. Run start-dev.cmd -CheckOnly.'
                continue
            }
            if (Test-ServicePortInUse $name) { continue }
            # Visible windows were requested; no hidden background server is created.
            Start-Process -FilePath $powershellPath -WorkingDirectory $projectRoot -WindowStyle Normal -ArgumentList @(
                '-NoProfile', '-NoExit', '-ExecutionPolicy', 'Bypass',
                '-File', ('"{0}"' -f $scriptPath), '-ChildService', $name
            ) | Out-Null
            Write-Host "Opened $name. Check its window for readiness or errors."
        }
        if ($Profile -eq 'without-nifi') {
            Write-Host 'without-nifi opened Kafka 3 nodes and two Spark Workers. Docker/NiFi was not started.'
        } else {
            Write-Host 'with-nifi opened Kafka 3 nodes, one Spark Worker, and NiFi Compose. Stop them with Ctrl+C in their service windows.'
        }
        return
    }

    $Host.UI.RawUI.WindowTitle = "Game-server | $ChildService"
    Set-Location -LiteralPath $projectRoot
    Write-Host "Starting $ChildService. Keep this window open. Stop with Ctrl+C."
    if (Test-ServicePortInUse $ChildService) { return }

    if ($ChildService -like 'kafka*') {
        $nodeNumber = [int]$ChildService.Substring(5)
        & (Join-Path $PSScriptRoot 'kafka.ps1') -Action start -Node $nodeNumber
    } elseif ($ChildService -like 'spark-*') {
        # Only these child PowerShell environments change, never the user's global settings.
        $env:SPARK_HOME = $sparkRoot
        $env:SPARK_CONF_DIR = Join-Path $sparkRoot 'conf'
        $env:SPARK_DAEMON_MEMORY = '192m'
        Set-Location -LiteralPath $sparkRoot
        if ($ChildService -eq 'spark-master') {
            & $sparkClass org.apache.spark.deploy.master.Master --host 127.0.0.1 --port 7077 --webui-port 8080
        } else {
            Write-Host 'Waiting up to 90 seconds for Spark Master port 7077...'
            $deadline = [DateTime]::UtcNow.AddSeconds(90)
            while (-not (Test-Listening 7077)) {
                if ([DateTime]::UtcNow -ge $deadline) { throw 'Spark Master is not ready. Check its window, then run start-dev.cmd again.' }
                Start-Sleep -Seconds 1
            }
            $workerNumber = [int]$ChildService.Substring('spark-worker'.Length)
            $workerPort = 7077 + $workerNumber
            $webPort = 8080 + $workerNumber
            $workPath = Join-Path $sparkRoot "work/worker-$workerNumber"
            & $sparkClass org.apache.spark.deploy.worker.Worker --host 127.0.0.1 --port $workerPort --webui-port $webPort --cores 4 --memory 768m --work-dir $workPath spark://127.0.0.1:7077
        }
    } else {
        if ($nifiPreflightIssues.Count -gt 0) {
            throw "NiFi Docker Compose preflight failed:`n- $($nifiPreflightIssues -join "`n- ")"
        }
        Set-Location -LiteralPath $nifiComposeRoot
        Write-Host "NiFi Compose: $nifiComposeFile"
        & $dockerCli compose --project-directory $nifiComposeRoot -f $nifiComposeFile up
    }
    if ($LASTEXITCODE -ne 0) { throw "$ChildService exited with code $LASTEXITCODE. Check the error above." }
} finally {
    if ($locked) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
