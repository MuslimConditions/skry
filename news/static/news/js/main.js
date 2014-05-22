$(document).ready(function(){
    if (history.pushState) {
        $('.card').click(function(event){
            event.preventDefault();
            $('article, #mask').show();
            window.originalScrollY = window.scrollY;
            $('#main').css({position: 'fixed', top: -window.originalScrollY})
            showArticle($(this).attr('data-id'));
        });
    }
    $('#mask').click(function(){
        $('article, #mask').hide();
        $('#main').css({position: '', top: ''})
        $(document).scrollTop(window.originalScrollY);
    });
});


function showArticle(id) {
    console.log(id);
    ajaxGet({id: id}, '/api/get_article_by_id/', function(response){
        console.log(response);
        // infobar
        $('article .category').html(response.category);
        $('article .publish-time').html(response.publish_time);
        $('article .publish-day').html(response.publish_day);
        // featured image
        if (response.featured_image) {
            $('article .featured-image img').prop('src', response.featured_image.url);
            $('article .featured-image figcaption').html(response.featured_image.caption);
            $('article .featured-image .credit .name').html(response.featured_image.credit);
            if (response.featured_image.courtesy)
                $('article .featured-image .courtesy').html('Courtesy of ');
            if (response.featured_image.organization)
                $('article .featured-image .organization').html(' / '+response.featured_image.organization);
        }
        // article content
        $('article .title').html(response.title);
        $('article .subhead').html(response.subhead);
        if (response.author)
            $('article .author').html('By ' + response.author);
        $('article .body').html(response.body).readingTime('.reading-time');
    });
}

/* utility functions */

function ajaxGet(params, endpoint, callback_success) {
    $.ajax({
        type: "GET",
        url: endpoint,
        data: params,
        crossDomain: true,
        success: callback_success,
        error: function(xhr, textStatus, errorThrown) {
            if (xhr.status != 0)
                console.error('Oh no! Something went wrong. Please report this error: \n'+errorThrown+xhr.status+xhr.responseText);
        }
    }); 
}

(function($) {
    /*!
    A simple version of:

    Name: Reading Time
    Dependencies: jQuery
    Author: Michael Lynch
    Author URL: http://michaelynch.com
    Date Created: August 14, 2013
    Date Updated: January 24, 2014
    Licensed under the MIT license

    */
    $.fn.readingTime = function(selector) {

        //return if no element was bound
        //so chained events can continue
        if(!this.length) { 
            return this; 
        }

        //define plugin
        var plugin = this;

        //define element
        var el = $(this);

        // words per minute
        var wpm = 270;

        var reading_time = Math.round(el.text().split(' ').length / wpm);

        // don't display anything if reading time is less that 30 secs
        if (reading_time < 1)
            return this;
        else
            $(selector).html(reading_time + ' min. read &ndash; ');
    }
})(jQuery);
