document.getElementById("top_5_profile_button").addEventListener("click", function() {
    //Create an AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/homepage/?top_5_type=profile");
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.onload = function() {
        // Handle the response from the server
        var response = xhr.responseText;
        console.log('hiiiiiiiiiiiiiiiiiiii');
        console.log(response);
        // const newurl = '/homepage/?top_5_type=profile';
        // window.location.href = newurl;
        if(xhr.status == 200)
        {
            window.location.href = '/homepage/?top_5_type=profile'
        }
    };
    xhr.send();
});

document.getElementById("top_5_current_button").addEventListener("click", function() {
    //Create an AJAX request
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/homepage/?top_5_type=current");
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.onload = function() {
        // Handle the response from the server
        var response = xhr.responseText;
        console.log('hiiiiiiiiiiiiiiiiiiii');
        console.log(response);
        // const newurl = '/homepage/?top_5_type=profile';
        // window.location.href = newurl;
        if(xhr.status == 200)
        {
            window.location.href = '/homepage/?top_5_type=current';
            //location.reload();
        }
    };
    xhr.send();
});


// Get all buttons with the class 'stock-button'
const buttons = document.querySelectorAll('.stock-button');

// Add a click event listener to each button
buttons.forEach(button => {
    button.addEventListener('click', async function() 
    {
        const stockname = this.getAttribute('data-name'); // get the ticker from the button's data attribute
        const response = await fetch('/get_stock_price_new/?stockname='+stockname); // send an AJAX request to the backend view
        const data = await response.json(); // parse the response JSON
        const ticker = data.stock_ticker;
        console.log(data.stock_ticker); // log the stock ticker to the console
        const test = await fetch('/homepage/?ticker='+ticker);
        console.log(test);

        // const newchart = await fetch('/predictionchart_ajax/?ticker='+ticker);
        // const datachart = await newchart.json();
        // var jsonString = JSON.stringify(datachart);
        // const chartresponse = datachart.predictionchart;
        // const encodedvalue = encodeURIComponent(chartresponse)
        // console.log(encodedvalue);
        // console.log(datachart.predictionchart);
        window.location.href = '?=ticker'+ticker; 
    });
});
