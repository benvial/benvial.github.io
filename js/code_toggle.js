
  function code_toggle() {
    if (code_shown){
      $('div.cm-s-jupyter').show('500');
      $('div.jp-OutputArea-executeResult').show('500');
      $('div.jp-OutputPrompt').show('500');
      $('#toggleButton').val('Hide Code')
    } else {
      $('div.cm-s-jupyter').hide('500');
        $('div.jp-OutputArea-executeResult').hide('500');
        $('div.jp-OutputPrompt').hide('500');
      $('#toggleButton').val('Show Code')
    }
    code_shown = !code_shown
  } 
  
  $( document ).ready(function(){
    code_shown=false; 
    $('#toggleButton').val('Hide Code')
    // $('div.jp-Cell').show()
  });
  
