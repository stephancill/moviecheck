$(document).ready(function() {
    $(window).trigger('resize');
})

$(".list-row .scroll-button").click(function() {
    $(".list-row")[0].scrollBy({
        left: 236,
        behavior: 'smooth'
    })
})

$(window).resize(function() {
    if ($(".list-row .movie").width() * $(".list-row .movie").length + $(".list-row .filler").width() > $(".list-row").width()) {
        $(".list-row .scroll-button").show()
    } else {
        $(".list-row .scroll-button").hide()
    }
}) 