
  function code_toggle() {
    if (code_shown){
      $('div.jp-Cell').hide('500');
      $('#toggleButton').val('Show Code')
    } else {
      $('div.jp-Cell').show('500');
      $('#toggleButton').val('Hide Code')
    }
    code_shown = !code_shown
  } 
  
  $( document ).ready(function(){
    code_shown=false; 
    $('div.jp-Cell').hide()
  });
  
  
// html.js.flexbox.flexboxlegacy.canvas.canvastext.webgl.no-touch.geolocation.postmessage.no-websqldatabase.indexeddb.hashchange.history.draganddrop.websockets.rgba.hsla.multiplebgs.backgroundsize.borderimage.borderradius.boxshadow.textshadow.opacity.cssanimations.csscolumns.cssgradients.no-cssreflections.csstransforms.csstransforms3d.csstransitions.fontface.generatedcontent.video.audio.localstorage.sessionstorage.webworkers.applicationcache.no-svg.no-inlinesvg.no-smil.no-svgclippaths body div.content section#portfolio div.container div#content.container div.row div#notebook.border-box-sizing div#notebook-container.container div.jp-Cell.jp-CodeCell.jp-Notebook-cell.jp-mod-noOutputs.celltag_rm_out div.jp-Cell-inputWrapper
