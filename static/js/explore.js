$(document).ready(function() {
    // TODO: Fix duplication here and in watchlist
    $(".movie-actions form").on("submit", function (e) {
        let form = $(this)
        e.preventDefault();
        const data = new FormData(form[0]);
        fetch(form.attr("action"), {
            method: form.attr("method"),
            body: data
        }).then(function(response) {
            if (response.status >= 200 && response.status < 300) {
                let url = form.attr("action")
                let formContainer = form.parents(".movie-actions")
                if (url.indexOf("add") !== -1) {
                    formContainer.addClass("watchlist")
                } else if (url.indexOf("seen") !== -1 || url.indexOf("remove") !== -1) {
                    formContainer.removeClass("watchlist")
                    formContainer.addClass("not-watchlist")
                }
            }
        })
    })
})