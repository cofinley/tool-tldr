function autoCompleteAjax(selector) {

    var xhr;
    new autoComplete({
        selector: selector,
        source: function (term, response) {
            try {
                xhr.abort();
            } catch (e) {
            }
            xhr = $.getJSON(window.location.origin + '/search', {q: term}, function (data) {
                response(data);
            });
        },
        renderItem: function (item, search) {
            var obj = item;
            item = obj.label;
            search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");
            return '<div class="autocomplete-suggestion" data-id="' + obj.id + '" data-type="' + obj.type + '">' + item.replace(re, "<b>$1</b>") + '</div>';
        },
        onSelect: function (e) {
            var itemData = e.srcElement.dataset;
            if (itemData.type === 't') {
                window.location.href = window.location.origin + '/tools?id=' + itemData.id;
            }
            else if (itemData.type === 'c') {
                window.location.href = window.location.origin + '/categories?id=' + itemData.id;
            }
        }
    });
}

autoCompleteAjax("#big-search-bar-input");
autoCompleteAjax("#search-input");