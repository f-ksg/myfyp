
const datalist = document.getElementById('datalistOptions');
const inputField = document.getElementById('searchDataList');
const tickerCodeField = document.getElementById('ticker-code');

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
$(window).ready(function () {
    $('#searchDataList').on('change', function () {

        //console.log('stock-ticker value change detected');
        var tickers = $('#ticker-code').val();
        //console.log(ticker);

        $.ajax
            ({
                url: '/get_stock_info/',
                data:

                    { 'ticker': tickers }

                ,
                dataType: 'json',
                success: function (data) {
                    {
                        //console.log('im in ajax call');
                        var ccurrentPrice = data.current_price;
                        // console.log(typeof currentPrice);
                        // console.log(currentPrice);
                        var n = ccurrentPrice.toFixed(3);

                        $('#currentprice').val(n);
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    errormessage = 'Stock has been de-listed';
                    console.log(errormessage);
                }
            });

        $.ajax
            ({
                url: '/get_chart_with_ticker/',
                data:
                    { 'ticker': tickers }
                ,
                dataType: 'json',
                success: function (data) {
                    {
                        //makeajax call to /get_new_chart/ sending ticker-code.val
                        //on succes add new chart data here
                        //success: function(data) <-- data is what im receiving
                        //var chartData = {{ chart|safe }};

                        //chartid = document.getElementById('chart');
                        //Plotly.newPlot(chartid, data);

                        //var data = JSON.parse(response.data);
                        var chartid = document.getElementById('chart');
                        console.log(chartid)
                        Plotly.newPlot(chartid, data);
                    }
                },
                error: function (xhr, textStatus, errorThrown) {
                    errormessage = 'chart error!';
                    console.log(errormessage);
                }
            });
    });
});


