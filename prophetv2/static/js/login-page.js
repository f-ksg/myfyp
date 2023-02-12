
(function ($) {
    "use strict";


    /*==================================================================
    [ Focus Contact2 ]*/
    $('.input100').each(function(){
        $(this).on('blur', function(){
            if($(this).val().trim() != "") {
                $(this).addClass('has-val');
            }
            else {
                $(this).removeClass('has-val');
            }
        })    
    })
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(){
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    

})(jQuery);



$('#registrationForm').on('submit', function(e)
{
    e.preventDefault();

    let isValid = true;

    // Validate name
    if($('#name').val().trim() == '')
    {
      $('#nameHelp').text('Name is required').show();
      isValid = false;
    }
    else{
        $('#nameHelp').hide();
    } 
// Validate email
if($('#email').val().trim() == '')
{
    $('#emailHelp').text('Email is required').show();
    isValid = false;
  } else if (!/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test($('#email').val().trim())){
    $('#emailHelp').text('Invalid email format').show();
    isValid = false;
  } else {
    $('#emailHelp').hide();
  }
  
  // Validate password
  if($('#password').val().trim() == ''){
    $('#passwordHelp').text('Password is required').show();
    isValid = false;
  } else {
    $('#passwordHelp').hide();
  }

  // If all fields are valid, submit the form
  if(isValid){
    // Submit the form
    // ...
    // Close the modal
    $('#registerModal').modal('hide');
  }
});

