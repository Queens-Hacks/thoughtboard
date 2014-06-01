
var connection = new ReconnectingWebSocket('ws://' + window.location.host + '/display/socket', ['soap', 'xmpp']);

connection.onmessage = function(e) {
  var data = JSON.parse(e.data);
  console.log('data', data)
  switch(data.key) {
    case 'new_sms': updateSms(data.val); break;
    case 'new_qr': updateQr(data.val); break;
    case 'new_message': updateMessage(data.val); break;
  }
}

var request = new XMLHttpRequest();
request.open('GET', '/display/info', true);
request.onload = function() {
  var initial_data = JSON.parse(request.responseText);
  updateSms(initial_data.smsCode);
  updateQr(initial_data.qrCode);
  updateMessage(initial_data.message);
}
request.send();

var smsValBox = document.getElementById('sms-code');
function updateSms(val) {
  smsValBox.innerHTML = val;
}

var qrCodeBox = document.getElementById('qr-code');
var HASH_ROOT = 'http://qhack.ca/the-best-idea-webapp/#';
var qrcode = new QRCode(qrCodeBox, {
    text: HASH_ROOT,
    width: 256,
    height: 256,
    colorDark : "#000000",
    colorLight : "#ffffff",
    correctLevel : QRCode.CorrectLevel.H
});
function updateQr(val) {
  qrcode.clear();
  var url = HASH_ROOT + val;
  qrcode.makeCode(url);
}

var messageBox = document.getElementById('message');
function updateMessage(val) {
  messageBox.innerHTML = val;
}
