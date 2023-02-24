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