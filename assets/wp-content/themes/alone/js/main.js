(function ($) {
    'use strict';

	$( document ).ready(function() {

		/**
		 * Extras navigation
		 */
     $('#site-extras-navigation .extra-item.toggle-item .toggle-icon').on('click', function(event) {
 			event.preventDefault();

      if( $(this).parent().hasClass('active') ) {
        $(this).parent().removeClass('active');
      } else {
        $('#site-extras-navigation .extra-item').removeClass('active');
        $(this).parent().addClass('active');
      }

 		});

    /**
		 * Header sticky
		 */
    if($( '.site-header .header-wrap' ).hasClass( 'header-sticky' )) {
      var header = $('.site-header'),
        	headerInfo = {top: header.offset().top, height: header.innerHeight()},
        	scrollTop = $(window).scrollTop();

      $(window).scroll(function() {
      	var currentScroll = $(window).scrollTop();

      	if(currentScroll > scrollTop) {
      		//console.log('scrollDown');
      		if (currentScroll > (headerInfo.top + headerInfo.height)){
      			$( '.site-header .sticky-branding' ).addClass('active');
            $( 'body' ).addClass('has-sticky-branding');
      		}
      	} else {
      		//console.log('scrollUp');
      		$( '.site-header .sticky-branding' ).removeClass('active');
          $( 'body' ).removeClass('has-sticky-branding');
      	}
      	scrollTop = currentScroll;
      });
 		}

    /**
		 * Scroll effect button back top
		 */
    if( $('#site-backtop').length ) {
      $('#site-backtop').on('click', function (event) {
          event.preventDefault();

          $('html, body').stop().animate({
                  scrollTop: 0
              },
              800
          );
      });
    }

    $('.progress-bar-container').each( function() {
      var bar = new ProgressBar.Line($(this)[0], {
        strokeWidth: 1,
        easing: 'easeInOut',
        duration: 800,
        color: '#FFEE00',
        trailColor: '#E8E8E8',
        trailWidth: 1,
        svgStyle: {width: '100%', height: '12px'},
        text: {
        style: {
          color: '#4D6995',
          position: 'absolute',
          right: '0',
          top: '28px',
          padding: 0,
          margin: 0,
          transform: null
        },
        autoStyleContainer: true
        },
        from: {color: '#FFEE00'},
        to: {color: '#FFEE00'},
        step: (state, bar) => {
          bar.setText(Math.round(bar.value() * 100) + ' %');
        }
      });

      var $barWidth = $(this).data('percent') / 100,

      waypoint = new Waypoint({
        element: $(this),
        handler: function() {
          bar.animate($barWidth);  // Number from 0.0 to 1.0
        },
        offset: '100%',
        triggerOnce: true
      });

    });

  });

})
(jQuery);
