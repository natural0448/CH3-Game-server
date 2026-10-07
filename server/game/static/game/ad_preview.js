const button = document.querySelector('#request-ad');
const nextRequestAt = new Map();
button.addEventListener('click', async () => {
  const message = document.querySelector('#message');
  const slot = document.querySelector('#slot').value;
  if (Date.now() < (nextRequestAt.get(slot) || 0)) { message.textContent = '같은 광고 위치는 15초 뒤 다시 요청해 주세요.'; return; }
  button.disabled = true;
  try {
    const csrfResponse = await fetch('/api/auth/csrf/', {credentials: 'same-origin'});
    const csrf = await csrfResponse.json();
    const response = await fetch('/api/ads/decision/', {method: 'POST', credentials: 'same-origin',
      headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrf.csrfToken},
      body: JSON.stringify({slot_id: slot})});
    const data = await response.json();
    if (!response.ok) throw new Error('광고를 받을 수 없습니다. 게임 로그인과 서버 연결을 확인하세요.');
    nextRequestAt.set(slot, Date.now() + 15000);
    if (data.ad === null) { document.querySelector('#ad').hidden = true; message.textContent = '이 위치에 선택할 광고가 없습니다.'; return; }
    const allowed = ['', '/static/ads/creatives/forest-tools.png', '/static/ads/creatives/camp-tea.png'];
    if (!allowed.includes(data.creative_path)) throw new Error('소재 경로를 확인하세요.');
    const image = document.querySelector('#creative');
    if (data.creative_path) {
      const loaded = new Image(); loaded.src = data.creative_path; await loaded.decode();
      image.src = data.creative_path;
    }
    image.hidden = !data.creative_path;
    document.querySelector('#title').textContent = data.title;
    document.querySelector('#body').textContent = data.body;
    document.querySelector('#receipt').textContent = data.campaign_id + ' · ' + data.bid_amount + ' 포인트 · 결정 ' + data.decision_id;
    document.querySelector('#ad').hidden = false;
    message.textContent = '광고 선택과 이미지 표시가 완료됐습니다. 노출 사건은 별도 실습에서 기록합니다.';
  } catch (error) { message.textContent = error.message; }
  finally { button.disabled = false; }
});
