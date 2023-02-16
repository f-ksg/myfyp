var stockprice = 0.0

const output = document.getElementById('unitsBuying');

output.addEventListener('keyup', (e) => 
{
    var units = parseFloat(document.getElementById('unitsBuying').value);
    var price = stockprice;
    var sum = units*price || 0;
    var stringSum = "$ " + sum;
    document.getElementById('totalPrice').value = stringSum;
});

$(document).ready(function() 
{
    $('#buyButton').click(function() {
        $.ajax({
            url: '/getStockPriceAjax/',
            type: 'GET',
            
            dataType: 'text',
            success: function(data) {
                stockprice = Number.parseFloat(data).toFixed(3);
                var stringStockPrice = "$ " + stockprice;
                $('#currentPrice').val(stringStockPrice);
                
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log('Error!');
            }
        });
    });
    
});

