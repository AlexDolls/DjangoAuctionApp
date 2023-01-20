const chatSocket = new WebSocket(`ws://${window.location.host}/ws/market/inbox/`)
/*chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/market/'
    + 'inbox'
    + '/'
);*/
chatSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.message) {
    document.querySelector('#inbox-message').innerHTML = data["user_inbox"];
  }
};

/*let sum_chat_unread = 0;
{% for chat_item in chats %}
{% for message_item in chat_item.message_set.all %}
{% if message_item.sender_id != user.id and message_item.unread %}
sum_chat_unread += 1;
{%
  endif %
}
{%
  endfor %
}
document.getElementById(`#numbers_chat_unread_{{chat_item.id}}`).innerHTML = sum_chat_unread;
sum_chat_unread = 0;
{%
  endfor %
}*/
//let n = 0;

/* Chat: change users' background on hover */
$(".chat-selection-line").mouseenter(function () {
  $(this).attr("class", "p-2 border-bottom chat-selection-line badge-primary-lighten");
}).mouseleave(function () {
  $(this).attr("class", "p-2 border-bottom chat-selection-line");
});