function autoCompleteAjax(selector) {

    var bigSize = selector !== "#search-input";
    var loaderDiv = bigSize ? '#big-loader' : '#small-loader';

    var xhr;
    new autoComplete({
        selector: selector,
        source: function (term, response) {
            $(loaderDiv).show();
            try { xhr.abort(); } catch (e){}
            xhr = $.getJSON(window.location.origin + '/search', {q: term}, function (data) {
                $(loaderDiv).hide();
                response(data);
            });
        },
        renderItem: function (item, search) {
            var obj = item;
            item = obj.label;
            search = search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            var re = new RegExp("(" + search.split(' ').join('|') + ")", "gi");

            var className = 'autocomplete-suggestion';
            if (bigSize) {
                className += ' autocomplete-suggestion-big';
            }

            var suggestionDiv = document.createElement('div');
            suggestionDiv.setAttribute('class', className);
            suggestionDiv.setAttribute('data-id', obj.id);
            suggestionDiv.setAttribute('data-type', obj.type);
            suggestionDiv.setAttribute('data-val', obj.label);
            suggestionDiv.innerHTML = item.replace(re, "<b>$1</b>");

            return suggestionDiv.outerHTML;
        },
        onSelect: function (e) {
            var itemData = e.target.dataset;
            if (itemData.type === 't') {
                window.location.href = window.location.origin + '/tools/' + itemData.id;
            }
            else if (itemData.type === 'c') {
                window.location.href = window.location.origin + '/categories/' + itemData.id;
            }
        }
    });
}

autoCompleteAjax("#big-search-bar-input");
autoCompleteAjax("#search-input");