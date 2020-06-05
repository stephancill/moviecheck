$(document).ready(function() {
    $(window).trigger('resize');
})

jQuery.fn.visible = function() {
    return this.css('visibility', 'visible');
};

jQuery.fn.invisible = function() {
    return this.css('visibility', 'hidden');
};

$(".list-row").scroll(function() {
    if ($(".list-row").scrollLeft() > $(".list-row .filler").width()) {
        $(".list-row .scroll-button.left").visible()
    } else {
        $(".list-row .scroll-button.left").invisible()
    }

    if (($(".list-row .movie").width() + 46) * $(".list-row .movie").length + 
    $(".list-row .filler").width() + $(".list-row .filler-end").width() < 
    $(".list-row").scrollLeft() + $(".list-row").width()) {
        $(".list-row .scroll-button.right").invisible()
    } else {
        $(".list-row .scroll-button.right").visible()
    }
})

$(".list-row .scroll-button.right").click(function() {
    $(".list-row")[0].scrollBy({
        left: 236,
        behavior: 'smooth'
    })
})

$(".list-row .scroll-button.left").click(function() {
    $(".list-row")[0].scrollBy({
        left: -236,
        behavior: 'smooth'
    })
})

$(window).resize(function() {
    $(".list-row .filler").css("min-width", ($(window).width() - $(".container").width())/2 - 40)

    if (($(".list-row .movie").width() + 46) * $(".list-row .movie").length + $(".list-row .filler").width() > $(".list-row").width()) {
        $(".list-row .scroll-button.right").visible()
    } else {
        $(".list-row .scroll-button.right").invisible()
    }
}) 