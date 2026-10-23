(function ($) {
    'use strict';

	$( document ).ready(function() {
    /**
     * Remove class active extra item
     */
     $('#site-extras-navigation .extra-item .give-btn').on('click', function(event) {
 			event.preventDefault();

      $('#site-extras-navigation .extra-item').removeClass('active');
    });

    $('.give-card__progress-custom .give-goal-progress').each( function() {

      if( ! $(this).parent().hasClass('give-card__progress-custom') || ! $(this).find('.give-progress-bar').length || $('body').hasClass('elementor-page') ) {
				return;
			}

      $(this).find('.give-progress-bar').css('display','none');

      var $type = $(this).parent().data('type'),
          $strokeWidth = $(this).parent().data('strokewidth'),
  				$easing = $(this).parent().data('easing'),
  				$duration = $(this).parent().data('duration'),
  				$color = $(this).parent().data('color'),
  				$trailColor = $(this).parent().data('trailcolor'),
  				$trailWidth = $(this).parent().data('trailwidth'),
  				$toColor = $(this).parent().data('tocolor'),
          $svgWidth = $(this).parent().data('width'),
					$svgHeight = $(this).parent().data('height');

          if( 'circle' === $type ) {
						var bar = new ProgressBar.Circle($(this)[0], {
						  strokeWidth: $strokeWidth,
						  easing: $easing,
						  duration: $duration,
						  color: $color,
						  trailColor: $trailColor,
						  trailWidth: $trailWidth,
						  svgStyle: {width: $svgWidth, height: $svgHeight},
						  from: {color: $color},
						  to: {color: $toColor},
						  step: (state, bar) => {
						    bar.path.setAttribute('stroke', state.color);
						  }
						});
					} else {
						var bar = new ProgressBar.Line($(this)[0], {
						  strokeWidth: $strokeWidth,
						  easing: $easing,
						  duration: $duration,
						  color: $color,
						  trailColor: $trailColor,
						  trailWidth: $trailWidth,
						  svgStyle: {width: $svgWidth, height: $svgHeight},
						  from: {color: $color},
						  to: {color: $toColor},
						  step: (state, bar) => {
						    bar.path.setAttribute('stroke', state.color);
						  }
						});
					}

					var $barWidth = $(this).find('.give-progress-bar').attr('aria-valuenow') / 100,

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
