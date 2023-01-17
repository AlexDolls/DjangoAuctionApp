/* Categories */
/* End Categories */

/* Chat */
/* End Chat */

/* Comment */

/* End Comment */



/* Create Listing */
function seturl(){
    document.getElementById("set-image-url").setAttribute("class", "btn btn-primary")
    document.getElementById("load-image-from-pc").setAttribute("class", "btn btn-secondary btn-light")
    document.getElementById("form-load-image").innerHTML = `
        <input type="text" class="form-control" id="imageurl" name="imageurl" placeholder="Enter image url">
    `
}

function loadfrompc() {
    document.getElementById("load-image-from-pc").setAttribute("class", "btn btn-primary")
    document.getElementById("set-image-url").setAttribute("class", "btn btn-secondary btn-light")
    document.getElementById("form-load-image").innerHTML = `
        <div class="input-group">
            <div class="custom-file">
                <input type="file" class="custom-file-input" id="loaded-imaged" name="loaded-imaged" placeholder="Choose image file">
            </div>
        </div>
    `
}

function checkallinputs(tellmewhy){
	const name_dom = document.getElementById("listingname");
	const category_dom = document.getElementById("listingcategory-input");
	const startprice_dom = document.getElementById("floatingInput");

	const name = (name_dom.value).replace(/\s+/g, ' ').trim();
	const category = category_dom.value;
	const startprice = (startprice_dom.value).replace(/\s+/g, ' ').trim();

	const submit_button = document.getElementById("submit-listing");

	const name_alarm = document.getElementById("name-alarm");
	const category_alarm = document.getElementById("category-alarm");
	const startprice_alarm = document.getElementById("startprice-alarm");

	if (tellmewhy === "0") {

		removealarm();

		if ((name != "")&&(category != "")&&(startprice != "")){
				submit_button.removeAttribute("disabled");
				submit_button.setAttribute("class", "btn btn-success btn-lg");
		} else{
				submit_button.setAttribute("disabled", "true");
				submit_button.setAttribute("class", "btn btn-secondary btn-lg");
		}
	} else {
		removealarm();

		if(name === ""){
			name_alarm.setAttribute("style","color:red;")
		}
		if(category === ""){
			category_alarm.setAttribute("style","color:red;")
		}
		if(startprice === ""){
			startprice_alarm.setAttribute("style", "color:red;")
		}
	}

}

$("#listingname").click(function(){
	checkallinputs("0");
});

$("#listingname").keyup(function(){
	checkallinputs("0");
});

$("#listingcategory-input").click(function(){
	checkallinputs("0");
});

$("#listingcategory-input").keyup(function(){
	checkallinputs("0");
});

$("#floatingInput").click(function(){
	checkallinputs("0");
});

$("#floatingInput").keyup(function(){
	checkallinputs("0");
});

$("#floatingTextarea2").click(function(){
	checkallinputs("0");
});

$("#floatingTextarea2").keyup(function(){
	checkallinputs("0");
});

$("#imageurl").click(function(){
	checkallinputs("0");
});

$("#imageurl").keyup(function(){
	checkallinputs("0");
});

$("#submit-button-block").click(function(){
	checkallinputs("1");
});
/* End Create Listing */

/* Detail */

// The Listing and server dates will be stored in a hidden input,
// so the value can be used as countdown variable.

let listingEndDate = document.getElementById("listing-end-date").value
let countDownDate = new Date(listingEndDate).getTime();

let serverDate = document.getElementById("server-date-now").value
let now = new Date(serverDate).getTime()

const listing_is_active = Boolean(document.getElementById("is_active").value);

let diff = countDownDate - now

const countDownInterval = setInterval(() => {

	diff = diff - 1000

	// Time calculations for days, hours, minutes and seconds
	let d = Math.floor(diff / (1000 * 60 * 60 * 24));
	let h = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
	let m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
	let s = Math.floor((diff % (1000 * 60)) / 1000);

	if (diff > 0) {
		document.getElementById("countdown-box").innerHTML=`${d}d ${h}h ${m}m ${s}s`;
	}

}, 1000)

// When countdown is over, display "EXPIRED", otherwise, display the countdown timer.
if (diff <= 0) {
	clearInterval(countDownInterval);
	document.getElementById("countdown-box").innerHTML = "EXPIRED";
} else {

}

function bidhistory() {

	/**
	 * Function that loads listing's bids info by REST API using AJAX
	 */

	const is_open = document.getElementById("is_open").getAttribute("value");

	if (is_open === "1"){
		const historyList = []

		$.ajax({
			type:"GET", url:"/market/api/"+listing_id+"/all_bids", success: (result) => {
				for (const bid_item in result){
					const username = result[bid_item].user.username;
					const bid_date = new Date(result[bid_item].date);
                    const value = result[bid_item].value;

					historyList.push(
						`
						<tr>
							<td class="previous-result">&#64;${username}</td>
							<td class="previous-result">${value}</td>
							<td class="previous-result">${bid_date}</td>
						</tr>
						`
					)
				}

				// Previous result is what placed on client's page
				const previous_result = document.getElementsByClassName("previous-result");
				const previous_result_length = previous_result.length;
				const historyList_length = historyList.length;

				// Add main HTML element for bids history list if no elements exists
				if (previous_result.length === 0) {
					const historyListTable = document.getElementById("history-list");
					historyListTable.innerHTML = `
						<table class="table table-centered mb-0">
							<thead>
								<tr>
									<th>User</th>
									<th>Last Bid</th>
									<th>Date</th>
								</tr>
							</thead>
							<tbody id="history-row">
							</tbody>
						</table>
					`
				}

				if (historyList_length !== previous_result_length) {
					// Add element differences to the page
                    for (let i = previous_result_length; i < historyList_length; i++) {
						document.getElementById("history-row").innerHTML += historyList[i];
					}

					const historyBtn = document.getElementById("history-btn");
					historyBtn.innerHTML = "Hide";
					historyBtn.onclick = () => clearhistory();
				}

				// If length of New result and previous same - just wait for next AJAX
				if ((document.getElementById("autoupdate").checked)) {
					setTimeout(() => {
						bidhistory()
					}, 5000);
				}
			}
        });
	}
}

function clearhistory() {
	const historyBtn = document.getElementById("history-btn");
	historyBtn.innerHTML = "Show";
	historyBtn.onclick = () => turn_is_open()

	document.getElementById("is_open").setAttribute("value", "0");
	document.getElementById("history-list").innerHTML = "";
}

function turn_is_open(){
	document.getElementById("is_open").setAttribute("value", "1");
	bidhistory();
}



const listing_id = document.getElementById("auction-listing-id").value;
const lastBid = document.getElementById("last-bid");
const newBid = document.querySelector('#newbid');
const listingSocket = new WebSocket(`ws://${window.location.host}/ws/market/${listing_id}/`);
/*listingSocket = new WebSocket(
	'ws://'
	+ window.location.host
	+ '/ws/market/'
	+ listing_id
	+ '/'
);*/

$(function() {
	listingSocket.onopen = (e) => {
		$.ajax({type:"GET", url:"/market/api/"+listing_id+"/last_bid", success:(result) => {
			if (result.value) {
				lastBid.value = result.value
			} else {
				const lastBidInfo = JSON.parse(result.data)
				lastBid.value = lastBidInfo.value
			}
		}});
	};
});

listingSocket.onmessage = (e) => {
	const data = JSON.parse(e.data);

	if (data.new_bid_set){
		lastBid.value = data.new_bid_set;
		//newBid.setAttribute('min', String(Number(data.new_bid_set + 0.01)));
		document.querySelector('#newbid').value = Number(data.new_bid_set)+0.01;

		// TODO: send a success message like, "Success!" and change class from danger to success
	}

	if (data.comment) {
		const newComment = document.getElementById("comment-box");
		newComment.innerHTML += `
			<div className="media">
				{% if comment.user.avatar %}
				<img
					src="{{ comment.user.avatar.url }}"
					alt=""
					className="mr-2 rounded"
					height="32"
				/>
				{% else %}
				<img
					src="https://www.meme-arsenal.com/memes/d0aea72a4f42092ccd20a17781d7df11.jpg"
					alt=""
					className="mr-2 rounded"
					height="32"
				/>
				{% endif %}
				<div className="media-body">
					<h5 className="m-0">${data.username}</h5>
					<p className="text-muted mb-0"><small>${data.comment_date}</small></p>
					<p className="my-1">${data.comment}</p>
				</div>
			</div>
			<hr>
		`
		document.getElementById('comment-input').value = "";

		const comments = document.getElementsByClassName("card comment")

		const scroll_check = document.querySelector('#autoscroll-check').checked
		if (scroll_check) {
			if (comments.length > 0) {
				comments[(comments.length-1)].scrollIntoView();
			}
		}

	}

	if (data.win_user_id) {
		const auctionListingId = document.getElementById("auction-listing-id").value;
		document.querySelector('#comment-input-form').innerHTML = "";

		if (data.user.id !== auctionListingId) {
			document.querySelector('#new-bid-block').innerHTML = "";
		}

		if (data.user.id === auctionListingId) {
			document.querySelector('#end-listing-block').innerHTML = "<h1>ENDED</h1>";
		}
		const current_user_id = "{{ user.id }}"


		if (current_user_id == data.win_user_id) {
			const winner_text = `<h2><strong>You're the winner of that listing!</strong></h2>`;
		} else {
			winner_text = "";
		}

		$.ajax({type:"GET", url:"/market/api/"+listing_id+"/last_bid", success:(result) => {
			if (result.value) {
				document.querySelector('#result').innerHTML =
				winner_text
				+"<center><h3><strong>"
				+ "Last Price: "
				+ "</strong>"
				+ result.value
				+ "</h3></center>"
				+ "<center><h2><span class = 'badge bg-warning'>"
				+ "Listing is Ended"
				+ "</span></h2></center>";
				document.querySelector('#end-listing-block').innerHTML = "";
			} else	{
				const last_bid_startbid = document.getElementById("listing-start-bid").value;
				document.querySelector('#result').innerHTML =
									"<h3><strong>"
									+ "Last Price: "
									+ "</strong>"
									+ last_bid_startbid
									+ " $</h3>"
									+ "<h2><span class = 'badge bg-warning'>"
									+ "Listing is Ended"
									+ "</span></h2>";
				document.querySelector('#end-listing-block').innerHTML = "";

			}
		}});
	}
};

listingSocket.onclose = (e) => {
	console.error("Listing details page connection was interrupted");
};



$(function(){
	$('#newbid').keyup(function(e){
		if (e.keyCode === 13) {
			$('#new-bid-submit').click()
		}
	});
});

$(function(){
	$('#new-bid-submit').click((e) => {
	const newbidInputDom = document.querySelector('#newbid');
				const newbid = newbidInputDom.value;
	const lastbidInputDom = document.querySelector('#last-bid');
	const lastbid = lastbidInputDom.value;
	if (isNaN(lastbid)) {
		compare_decision = 1;
	} else {
		if ((Number(newbid) > Number(lastbid)) && (Number(newbid)<=99999.99)){
			compare_decision = 1;
		}
		else {
			compare_decision = 0;
			if (Number(newbid) < Number(lastbid)){
				document.querySelector("#bid-warning").innerHTML = "Value must be bigger than last bid";
				document.querySelector('#newbid').value = Number(lastbid)+1;
			} else {
				document.querySelector("#bid-warning").innerHTML = "Value must be less or equal 99999.99";
				document.querySelector('#newbid').value = Number(lastbid)+1;
			}
		}
	}

	if (compare_decision == 1) {
		document.querySelector("#bid-warning").innerHTML = "";
		listingSocket.send(JSON.stringify({ 'newbid': newbid, 'listing_id':listing_id }));
	}});
});

$(function(){
	$('#comment-input').keyup(function(e){
		if (e.keyCode === 13){
			$('#comment-submit').click()
		}
	});
});


$(function(){
	$('#comment-submit').click(function(e){
		const newCommentDom = document.querySelector('#comment-input');
		const newComment = newCommentDom.value;
		listingSocket.send(JSON.stringify({ 'post_comment': newComment, 'listing_id':listing_id }));
	});
});

$(function(){
	$('#end-listing-submit').click(function(e) {
		const endlisting = 'end';
		listingSocket.send(JSON.stringify({ 'endlisting':endlisting, 'listing_id':listing_id, }));
	});
});
/* End Detail */
