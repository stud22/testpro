(function(){
    var jquery_version = '2.1.4';
    var site_url = 'http://127.0.0.1:8000/';
    var static_url = site_url + 'static/images/';
    var min_width = 10;
    var min_height = 10000;
    var jquery_url = static_url+'js/jquery.min.js';

    function bookmarklet(msg){
        var css = jQuery('<link>');
        css.attr({
            rel: 'stylesheet',
            type: 'text/css',
            href: static_url+'css/bookmarklet.css?r='+Math.floor(Math.random() * 8989899)
        });
        jQuery('head').append(css);
        box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>Select an image to bookmark:</h1><div class="images"></div></div>';
        jQuery('body').append(box_html);
        jQuery('#bookmarklet #close').click(function(){
            jQuery('#bookmarklet').remove();
        });
        jQuery.each(jQuery('img'), function(index, image){
            console.log(image);
            //if (jQuery(image).width()>=min_width && jQuery(image).height()>=min_height){
                image_url = jQuery(image).attr('src');
                jQuery('#bookmarklet .images').append('<a href="#"><img src="'+image_url+'"/></a>');
           // }
        });

        jQuery('#bookmarklet .images a').click(function(e){
            e.preventDefault();
            selected_image = jQuery(this).children('img').attr('src');
            jQuery('#bookmarklet').hide();
            window.open(site_url+'images/create/?url=' + encodeURIComponent(selected_image)
                                                    + '&title='
                                                    +encodeURIComponent(jQuery('title').text()),
                                                    '_blank');
        });

    };

    if (typeof window.jQuery != 'undefined'){
        bookmarklet();
    }else{
        var conflict = typeof window.$ != 'undefined';
        var script = document.createElement('script');
        script.setAttribute('src', jquery_url);
        document.getElementsByTagName('head')[0].appendChild(script);
        var attempts = 15;
        (function(){
            if(typeof window.jQuery == 'undefined'){
                if(--attempts>0){
                    window.setTimeout(arguments.callee, 250);
                }else{
                    alert('An error occured while loading jquery');
                }
            }else{
                bookmarklet();
            }
        })();
    }
})();
