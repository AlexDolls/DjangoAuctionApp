// const chatSocket = new WebSocket(`ws://${window.location.host}/ws/market/inbox/`)
/*chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/market/'
    + 'inbox'
    + '/'
);*/
/*
function getChat(chat_id) {
  console.log(chat_id)
  $.ajax({type:"GET", url:`/market/api/chat/${chat_id}`, success:(result) => {
    console.log("RESULT", result)
  }});
}
*/
/*
chatSocket.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log("DATA", data)

  if (data.message) {
    document.querySelector('#inbox-message').innerHTML = data["user_inbox"];
  }
};*/
/*
chatSocket.onopen = (e) => {
  $.ajax({type:"GET", url:`/market/api/${listing_id}/last_bid`, success:(result) => {
    if (result.value) {
    lastBid.value = result.value
    } else {
      const lastBidInfo = JSON.parse(result.data)
      lastBid.value = lastBidInfo.value
    }
  }});
}*/



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
/*
$(".inbox-list-user").mouseenter(function () {
  $(this).attr("class", "media bg-light p-2 inbox-list-user");
}).mouseleave(function () {
  $(this).attr("class", "media mt-1 p-2 inbox-list-user");
});

$(".inbox-list-user").onclick(function () {
  console.log("YOU CLICKED!")
})
*/
