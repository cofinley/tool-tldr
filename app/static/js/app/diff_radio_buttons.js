$(".radio-left").click(function (){
    var leftIndex = $('input[name=inlineRadioOptionsLeft]:checked').index("input[name=inlineRadioOptionsLeft]");
    $(".radio-right").each(function(idx, obj){
        if (idx > leftIndex - 1){
            $(obj).css("visibility", "hidden");
            $(obj).prop("disabled", true);
        }
        else {
            $(obj).css("visibility", "visible");
            $(obj).prop("disabled", false);
        }
    });
});

$(".radio-right").click(function (){
    var rightIndex = $('input[name=inlineRadioOptionsRight]:checked').index("input[name=inlineRadioOptionsRight]");
    $(".radio-left").each(function(idx, obj){
        if (idx <= rightIndex){
            $(obj).css("visibility", "hidden");
            $(obj).prop("disabled", true);
        }
        else {
            $(obj).css("visibility", "visible");
            $(obj).prop("disabled", false);
        }
    });
});

$("#compare-selected").click(function() {
    var type = this.dataset.type;
    var id = this.dataset.id;
    var older = $('input[name=inlineRadioOptionsLeft]:checked').val();
    var newer = $('input[name=inlineRadioOptionsRight]:checked').val();
    window.location.href = window.location.origin + "/" + type + "/" + id + "/edits/diff/" + older + "/" + newer;
});
