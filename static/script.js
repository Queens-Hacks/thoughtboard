
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
