
const datalist = document.getElementById('datalistOptions');
const inputField = document.getElementById('searchDataList');
const tickerCodeField = document.getElementById('ticker-code');
const url = `/get_chart_with_ticker/?ticker=${tickerCodeField}`; // Construct the URL with the ticker code


inputField.addEventListener('input', () => {
    // Clear the value of the ticker code field when the input field changes
    tickerCodeField.value = '';
});

inputField.addEventListener('change', () => {
    // Get the selected option from the datalist
    const selectedOption = datalist.querySelector(`option[value='${inputField.value}']`);

    // Set the value of the ticker code field to the value of the selected option
    tickerCodeField.value = selectedOption.value.split(' ').pop();
});

// $(document).ready(function () 
// {
//     var ccurrentPrice = data.current_price;
//     // console.log(typeof currentPrice);
//     // console.log(currentPrice);
//     var n = ccurrentPrice.toFixed(3);
//     $('#currentprice').val(n);
// });

//get current price and display
$(document).ready(function () 
{
    $('#searchDataList').on('change', function () 
    {

        //console.log('stock-ticker value change detected');
        var tickers = $('#ticker-code').val();
        var csrftoken = Cookies.get('csrftoken');
        //console.log(ticker);
        //for retrieval of price and setting price of stock 
        $.ajax
            ({
                url: '/get_stock_info/',
                data:
                    { 'ticker': tickers }
                ,
                dataType: 'json',
                success: function (data) {
                    {
                    const newurl = `/purchase/?ticker=${tickerCodeField.value}`;
                    // Open the URL in a new tab
                    window.location.href = newurl;
                    $(document).ready(function () {
                    //console.log('im in ajax call');
                    var ccurrentPrice = data.current_price;
                    // console.log(typeof currentPrice);
                    // console.log(currentPrice);
                    var n = ccurrentPrice.toFixed(3);
                    $('#currentprice').val(n);
                    });
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    errormessage = 'Stock has been de-listed';
                    $('#currentprice').val('No value found');
                    console.log(errormessage);
                }
            });

        //attempt to generate new chart on same website F
        $.ajax
            ({
                type: "POST",
                url: "/purchase/",
                data: "ticker=" + encodeURIComponent(tickers),
                dataType: 'text',
                beforeSend: function(xhr, settings) {
                    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    }
                },
                success: function(data) {
                    console.log('hey im here')
                    const newurl = `/purchase/?ticker=${tickerCodeField.value}`;
                    // Open the URL in a new tab
                    window.location.href = url;
                },
                error: function(xhr, textStatus, errorThrown) {
                    errormessage = 'current price chart error!';
                    console.log('eh fail leh')
                    //alert('unable to retrieve stock price');
    }
            });
    });

});

var buybutton = document.getElementById('buyButton');

buybutton.addEventListener('click', () => {
    var datalist = document.getElementById('stock-name');
    var buystockform = document.getElementById('stock-ticker');
    // Get the URL query string
    const queryString = window.location.search;

    // Extract the value of the 'code' parameter
    const codeParam = new URLSearchParams(queryString).get('ticker');

    // Remove the '.SI' suffix if it exists
    const code = codeParam ? codeParam.replace('.SI', '') : '';

    // Use the 'code' variable as needed
    console.log(code);

    const testoption = [...datalist.options].find((option) => option.value.includes(code));
    console.log(testoption);
    if (testoption) 
    {
        testoption.selected = true;
        tickerCodeField.value = testoption.value.split(' ').pop();
        console.log(tickerCodeField.value);
        buystockform.value = tickerCodeField.value + '.SI';
        var currentpriceform = document.getElementById('current-price');
        currentpriceform.value = document.getElementById('currentprice').value;
    }
});


const totalprice = document.getElementById('units-buying');

totalprice.addEventListener('keyup', (e) => 
{
    var units = parseFloat(document.getElementById('units-buying').value);
    console.log(units);
    //regex to strip $ and save .
    var price = document.getElementById('current-price').value.replace(/[^\d.-]/g, '');
    console.log(price);
    var sum = units*price || 0;
    var summy = Math.round(sum*100)/100;
    // var stringSum = "$ " + summy;
    document.getElementById('total-price').value = '$' + summy;
    
});