
var connection = new WebSocket('ws://' + window.location.host + '/display/socket', ['soap', 'xmpp']);

connection.onmessage = function(e) {
  switch(e.key) {
    case 'new_sms': updateSms(e.val); break;
    case 'new_qr': updateQr(e.val); break;
    case 'new_message': updateMessage(e.val); break;
  }
  console.log('got', e.data)
}


var smsValBox = document.getElementById('sms-code');
function updateSms(val) {
  smsValBox.innerHTML = val;
}

var qrCodeBox = document.getElementById('qr-code');
function updateQr(val) {
  qrCodeBox.innerHTML = val;
}

var messageBox = document.getElementById('message');
function updateMessage(val) {
  messageBox.innerHTML = val;
}
