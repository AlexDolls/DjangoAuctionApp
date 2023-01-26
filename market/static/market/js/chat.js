const chatSocket = new WebSocket(`ws://${window.location.host}/ws/market/inbox/`)

const scroll_check = document.querySelector("#autoscroll-check").checked;
const listBox = document.getElementById("messages-field")
if (scroll_check) {
  listBox.scrollIntoView({behavior: "smooth", block: "end"})
}

const chatId = document.getElementById("chat-id").value

chatSocket.onmessage = function (e) {
  /**
   * Parse data to update message box.
   */

  const data = JSON.parse(e.data);

  if (data["message"]) {
    if (data["send_self"]) {
      const msgBox = document.getElementById("messages-field")

      msgBox.innerHTML +=
          `
            <li class="clearfix odd">
              <div class="text-right">
                <i>${data['message_date']}</i>
              </div>
              <div class="chat-avatar">
                <img src="${data['user']['avatar']['url']}" class="rounded" alt=""/>
              </div>
              <div class="conversation-text">
                <div class="ctext-wrap">
                  <i>${data['sender']}</i>
                  <p>${data['message']}</p>
                </div>
              </div>
            </li>
          `

      if (scroll_check) {
        listBox.scrollIntoView({behavior: "smooth", block: "end"})
      }
    }
  }
};

$('#message-input').keyup(function(e){
  if (e.keyCode === 13){
    $('#message-submit').click()
  }
});

$("#message-submit").click(function(e) {
  const message = document.getElementById("message-input")

  chatSocket.send(JSON.stringify({
    chat_id: chatId,
    new_message_text: message.value,
  }));
})

chatSocket.onclose = function (e) {
  console.error("Chat socket closed unexpectedly");
};