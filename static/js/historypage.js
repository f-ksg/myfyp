window.addEventListener('DOMContentLoaded', event => {
    
    const historydatatables = document.getElementById('stock-table');
    if (historydatatables) 
    {
        new simpleDatatables.DataTable(historydatatables);
    }

    const solddatatables = document.getElementById('stock-table-2');
    if (solddatatables) 
    {
        new simpleDatatables.DataTable(solddatatables);
    }

});
