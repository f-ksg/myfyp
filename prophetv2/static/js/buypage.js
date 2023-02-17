// var stockprice = 0.0

const output = document.getElementById('units-buying');

output.addEventListener('keyup', (e) => 
{
    var units = parseFloat(document.getElementById('units-buying').value);
    var price = document.getElementById('current-price').value;
    var sum = units*price || 0;
    var summy = Math.round(sum*100)/100;
    // var stringSum = "$ " + summy;
    document.getElementById('total-price').value = summy;
});

var stockNameDropdown = document.getElementById("stock-name");

// listen to stock-name change
stockNameDropdown.addEventListener("change", function() 
{
  // Get the selected option from the stock name dropdown
  var selectedOption = stockNameDropdown.options[stockNameDropdown.selectedIndex];

  // Get the value of the selected option
  var selectedValue = selectedOption.value;

  // Get the stock ticker input element
  var stockTickerInput = document.getElementById("stock-ticker");

  // Set the value of the stock ticker input element to the ticker value from the selected stock
  var stockCode = selectedOption.text.match(/\(([^)]+)\)/)[1];
  var resultString = stockCode.concat(".SI");
  
  var ticker = $('#stock-ticker');
  stockTickerInput.value = resultString
 });

 //listen to stock-name change
 $(document).ready(function() 
 {
    $('#stock-name').on('change', function() 
    {
      //console.log('stock-ticker value change detected');
      var ticker = $('#stock-ticker').val();
      //console.log(ticker);
      $.ajax({
        url: '/get_stock_info/',
        data: 

        {'ticker':ticker}

        ,
        dataType: 'json',
        success: function(data) 
        {
          //console.log('im in ajax call');
          var currentPrice = data.current_price;
          // console.log(typeof currentPrice);
          // console.log(currentPrice);
          var n = currentPrice.toFixed(3);
          $('#current-price').val(n);
        },
        error: function(xhr, textStatus, errorThrown) 
        {
          errormessage = 'Stock has been de-listed';
          console.log('Error!');
        }
      });
    });
  });

