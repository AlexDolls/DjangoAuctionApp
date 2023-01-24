// The Listing and server dates will be stored in a hidden input,
// so the value can be used as countdown variable.

const lastBid = document.getElementById("listing-last-bid")
const listing_id = document.getElementById("auction-listing-id").value;
const listingSocket = new WebSocket(`ws://${window.location.host}/ws/market/${listing_id}/`);

const listingEndDate = document.getElementById("listing-end-date").value
const countDownDate = new Date(listingEndDate).getTime()

const serverDate = document.getElementById("server-date-now").value
const now = new Date(serverDate).getTime()

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
}

function bidhistory() {

	/**
	 * Function that loads listing's bids info by REST API using AJAX
	 */

	const is_open = document.getElementById("is_open").value;
	const listing_id = document.getElementById("auction-listing-id").value;

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
						<table class="table table-bordered table-centered mb-0">
							<h4 class="mt-0 text-primary">History</h4>
							<thead class="thead-light">
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




$(function(){
	/**
	 * Roles inside this function:
	 * 1. Enter will be accepted as "click".
	 * 2. End a Listing.
	 * 3. Update Last Bid
	 */

	$('#newbid').keyup(function(e){
		if (e.keyCode === 13) {
			$('#new-bid-submit').click()
		}
	});

	$('#comment-input').keyup(function(e){
		if (e.keyCode === 13){
			$('#comment-submit').click()
		}
	});

	$('#end-listing-submit').click(function(e) {
		const endlisting = 'end';
		listingSocket.send(JSON.stringify({ 'endlisting':endlisting, 'listing_id':listing_id, }));
	});

	listingSocket.onopen = (e) => {
		$.ajax({type:"GET", url:`/market/api/${listing_id}/last_bid`,
			success:(result) => {
				if (result.value) {
				lastBid.value = result.value
				} else {
					const lastBidInfo = JSON.parse(result.data)
					lastBid.value = lastBidInfo.value
				}
			}
		});
	};
});

function makeBid() {
	/**
	 * Try to make a bid on click.
	 * Verify requirements for bid.
	 * Send a success message and update last bid value on table.
	 * Otherwise, send an error message to alert user.
	 */

	const newBid = document.getElementById("newbid")
	const bidAlert = document.getElementById("bid-warning")

	const minValue = lastBid.value
	const maxValue = 99999
	let is_approved

	if (newBid.value > minValue && newBid.value < maxValue) {
		is_approved = true
	} else {
		if (newBid.value <= minValue || newBid.value > maxValue) {
			is_approved = false
		}
	}

	if (is_approved) {
		listingSocket.send(JSON.stringify({
			"newbid": newBid.value,
			"listing_id": listing_id
		}));

		bidAlert.innerHTML = `
			<div class="alert alert-success alert-dismissible 
			bg-success text-white border-0 fade show" 
			role="success">
				<button type="button" class="close" data-dismiss="alert" aria-label="Close">
					<span aria-hidden="true">&times;</span>
				</button>
				<strong>Success! </strong>You made a bid
			</div>
		`
		document.getElementById("listing-last-bid-input").innerHTML = newBid.value
		const newMinValue = Number(newBid.value) + 0.01
		newBid.value = newMinValue.toFixed(2)
	} else {
		bidAlert.innerHTML = `
			<div class="alert alert-danger alert-dismissible bg-danger text-white border-0 fade show" role="alert">
				<button type="button" class="close" data-dismiss="alert" aria-label="Close">
					<span aria-hidden="true">&times;</span>
				</button>
				<strong>Error! </strong>Value must be bigger than last bid and less than or equal to 99999
			</div>
		`
	}
}

function makeComment() {
	/**
	 * Try to make a new comment.
	 * Empty comments won't be accepted.
	 * Alerts for 'success' or 'error' will be send to user.
	 * If successfull, a new comment will be added to the end of the list.
	 */

	const newCommentInput = document.getElementById("comment-input").value
	const commentTitle = document.getElementById("comment-title")
	const commentLenght = Number(document.getElementById("comments-length").value)
	const newCommentValue = newCommentInput.trim()
	const commentAlert = document.getElementById("comment-alert")

	if (newCommentValue) {
		listingSocket.send(JSON.stringify({
			"post_comment": newCommentInput,
			"listing_id": listing_id
		}));

		commentTitle.innerHTML = `Comments (${ commentLenght + 1})`
		commentAlert.innerHTML = `
			<div class="alert alert-success alert-dismissible bg-success text-white border-0 fade show" role="alert">
				<button type="button" class="close" data-dismiss="alert" aria-label="Close">
					<span aria-hidden="true">&times;</span>
				</button>
				<strong>Success! </strong>You can't make an empty comment.
			</div>
		`
	} else {
		commentAlert.innerHTML = `
			<div class="alert alert-danger alert-dismissible bg-danger text-white border-0 fade show" role="alert">
				<button type="button" class="close" data-dismiss="alert" aria-label="Close">
					<span aria-hidden="true">&times;</span>
				</button>
				<strong>Error! </strong>You can't make an empty comment.
			</div>
		`
	}
}

listingSocket.onmessage = (e) => {
	const data = JSON.parse(e.data);

	if (data["new_bid_set"]) {
		lastBid.value = data["new_bid_set"];
	}

	if (data["comment"]) {
		const commentBox = document.getElementById("comment-box");

		const newComment = document.createElement("div")
		newComment.innerHTML +=`
			<div class="media mt-2">
				<img class="mr-3 avatar-sm rounded-circle"
					 alt=""
					 src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fwww.pngall.com%2Fwp-content%2Fuploads%2F5%2FProfile-PNG-Image-180x180.png"/>
				<div class="media-body">
					<h5 class="mt-0">
						&#64;${data["username"]}
						<i>${data["comment_date"]}</i>
					</h5>
					<p class>${data["comment"]}</p>
				</div>
			</div>
		`
		commentBox.appendChild(newComment);
		document.getElementById('comment-input').value = "";

		const comments = document.getElementsByClassName("card comment")

		const scroll_check = document.querySelector('#autoscroll-check').checked
		if (scroll_check) {
			if (comments.length > 0) {
				comments[(comments.length-1)].scrollIntoView();
			}
		}
	}

	/*if (data["win_user_id"]) {
		const auctionListingId = document.getElementById("auction-listing-id").value;
		document.querySelector('#comment-input-form').innerHTML = "";

		if (data.user.id !== auctionListingId) {
			document.querySelector('#new-bid-block').innerHTML = "";
		}

		if (data.user.id === auctionListingId) {
			document.querySelector('#end-listing-block').innerHTML = "<h1>ENDED</h1>";
		}
		const current_user_id = "{{ user.id }}"


		if (current_user_id === data["win_user_id"]) {
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
	}*/
};

listingSocket.onclose = (e) => {
	console.error("Listing details page connection was interrupted");
};