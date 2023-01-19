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
		<input type="file" class="form-control" id="loaded-image" 
		name="loaded-image" aria-describedby="inputGroupFileAddon04" 
		aria-label="Upload">
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