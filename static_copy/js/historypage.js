window.addEventListener('DOMContentLoaded', event => {
    
    const historydatatables = document.getElementById('stock-table');
    if (historydatatables) 
    {
        new simpleDatatables.DataTable(historydatatables);
    }
});
