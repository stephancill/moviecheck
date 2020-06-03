$(document).ready(function() {
    $(".movie form").on("submit", function (e) {
        let form = $(this)
        e.preventDefault();
        const data = new FormData(form[0]);
        fetch(form.attr("action"), {
            method: form.attr("method"),
            body: data
        }).then(function(response) {
            if (response.status >= 200 && response.status < 300) {
                location.reload()
            }
        })
    })
    
    $(".watchlist-row .scroll-button").click(function() {
        $(".watchlist-row")[0].scrollBy({
            left: 236,
            behavior: 'smooth'
        })
    })
    console.log($(".watchlist-row .movie").length * 236)
    $(window).trigger('resize');
})

$(window).resize(function() {
    console.log($(".watchlist-row .movie").length * 236, $(".watchlist-container").width())
    if ($(".watchlist-row .movie").length * 236 - $(".watchlist-row .filler").width() > $(".watchlist-container").width()) {
        $(".watchlist-row .scroll-button").show()
    } else {
        $(".watchlist-row .scroll-button").hide()
    }
}) 