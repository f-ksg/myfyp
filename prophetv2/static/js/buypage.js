var stockprice = 0.0

const output = document.getElementById('unitsBuying');

output.addEventListener('keyup', (e) => 
{
    var units = parseFloat(document.getElementById('unitsBuying').value);
    var price = stockprice;
    var sum = units*price || 0;
    document.getElementById('totalPrice').value = sum;
});

$(document).ready(function() 
{
    $('#buyButton').click(function() {
        $.ajax({
            url: '/getStockPriceAjax/',
            type: 'GET',
            
            dataType: 'text',
            success: function(data) {
                $('#currentPrice').val(data);
                stockprice = parseFloat(data);
            },
            error: function(xhr, textStatus, errorThrown) {
                console.log('Error!');
            }
        });
    });
});

