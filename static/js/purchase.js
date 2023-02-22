
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
                    console.log('hey im here');
                    const newurl = `/purchase/?ticker=${tickerCodeField.val()}`;
                    // Open the URL in a new tab
                    //window.location.href = url;
                },
                error: function(xhr, textStatus, errorThrown) {
                    errormessage = 'current price chart error!';
                    console.log(errormessage);
                    //alert('unable to retrieve stock price');
    }
            });
    });

});

//-----------------------for django buy model form----------------------
const units_buying = document.getElementById('id_units_buying');
units_buying.addEventListener('keyup', (e) => 
{

    var units = parseFloat(document.getElementById('id_units_buying').value);
    console.log(units);
    //regex to strip $ and save .
    var price = document.getElementById('id_purchase_price').value.replace(/[^\d.-]/g, '');
    console.log(price);
    var sum = units*price || 0;
    var summy = Math.round(sum*100)/100;
    // var stringSum = "$ " + summy;
    document.getElementById('id_total_price').value = summy;
});


var buyyButton = document.getElementById('buyButton');
buyyButton.addEventListener('click', () => 
{
    document.getElementById('id_total_price').readOnly = true;
    //var datalist = document.getElementById('id_stock');
    var buystockform = document.getElementById('stock-ticker');
    // Get the URL query string
    const queryString = window.location.search;

    // Extract the value of the 'code' parameter
    const codeParam = new URLSearchParams(queryString).get('ticker');

    // Remove the '.SI' suffix if it exists
    const code = codeParam ? codeParam.replace('.SI', '') : '';

    // Use the 'code' variable as needed
    console.log(code);

    stockchoice = document.getElementById('id_stock');
    //print(stockchoice);
    // Check if a choice contains the partial string
    for (let i = 0; i < stockchoice.options.length; i++) {
        const option = stockchoice.options[i];
        if (option.textContent.includes(code)) 
        {
          option.selected = true;
          break;
        }
      }
   
    var currentpriceform = document.getElementById('id_purchase_price');
    currentpriceform.value = document.getElementById('currentprice').value.replace('$', '');
    
});
//--------------------end django buy model form----------------------

//-----------------------for django sell model form----------------------
//get quantity of stocks owned
$(document).ready(function() {
    $('#id_stock_owned').change(function() {
        // Retrieve the selected stock's ID
        var stock_id = $(this).val();
        // Make an AJAX request to retrieve the stock's quantity
        $.get('/get-stock-quantity/', {'stock_id': stock_id}, function(data) {
            // Update the quantity field with the retrieved quantity
            console.log(data);
            $('#id_sell_quantity').val(data.quantity);
        });
        
        //get current price
        const id_stock_owned_value = $("#id_stock_owned").val();
        const stockname = $("#id_stock_owned option:selected").text();
        $.get('/get_stock_price_new/', 
        {'stockname': stockname}, 
        function(data) 
        {
            console.log(data);
            $('#id_sell_price').val(data.price);
        });

    });
});



const units_selling = document.getElementById('id_units_selling');
units_selling.addEventListener('keyup', (e) => 
{
    console.log('im here pressing');
    var units = parseFloat(document.getElementById('id_units_selling').value);
    console.log(units);
    //regex to strip $ and save .
    var price = document.getElementById('id_sell_price').value.replace(/[^\d.-]/g, '');
    console.log(price);
    var sum = units*price || 0;
    var summy = Math.round(sum*100)/100;
    // var stringSum = "$ " + summy;
    document.getElementById('id_sell_total_price').value = summy;
});


//-------------------------------------------------------------------------