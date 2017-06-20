$(function () {
  $("div.alert button.close").click(function (){
      $("div.alert").first().remove();
    });
});