( function( $ ) {
	/**
 	 * @param $scope The Widget wrapper element as a jQuery element
	 * @param $ The jQuery alias
	 */
	var CounterHandler = function( $scope, $ ) {
		//console.log($scope);
 		var $selector = $scope.find('.elementor-counter__number'),
 				$dataCounter  = $selector.data('counter'),
				waypoint = new Waypoint({
				  element: $selector,
				  handler: function() {
						$selector.numerator( $dataCounter );
				  },
					offset: '100%',
					triggerOnce: true
				});

 	};

	var CountDownHandler = function( $scope, $ ) {
		//console.log($scope);
		$scope.find('.countdown').each( function() {
			var $countdownTime = $(this).attr('data-countdown'),
					$countdownFormat = $(this).attr('data-format');

			$(this).countdown({
				until: $countdownTime,
				format: $countdownFormat,
				padZeroes: true
			});

		});
 	};

	var MagnificPopupHandler = function( $scope, $ ) {
		//console.log($scope);
		$scope.find('.elementor-open-popup-link').magnificPopup({
		  type:'inline',
		  midClick: true
		});

 	};

	var FilterPostHandler = function( $scope, $ ) {
		//console.log($scope);
		// Get all items
		var items = [];
		$scope.find('.elementor-item').each(function() {
			items.push('<div class="animate__hide ' + $(this).attr('class') + '" data-group="' + $(this).data('group') + '">' + $(this).html() + '</div>');
		});

		// click filter navigation
		$scope.find('.elementor-filter a').click(function (e) {
			e.preventDefault();
			if ($(this).hasClass('active')) {
        return;
      }

      $('.elementor-filter a').removeClass('active');
      $(this).addClass('active');

			var group = $(this).data('filter');
			$scope.find('.elementor-item').addClass('animate__hide');
			$scope.find('.elementor-item').one('webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend', function() {
				$scope.find('.elementor-grid').html(''); // empty list content

				// get filter result
				var result = '';
        if ( 'all' === group ) {
          result = items;
        } else {
          for (var i = 0; i < items.length; i++) {
  					if ($(items[i]).data('group').split(' ').includes(group)) {
  						result += items[i];
  					}
  				};
        }

				if ('' === result ) {
          result += '<div class="elementor-' + $scope.find('.elementor-filter').data('type') + ' elementor-item no-result" data-group="' + group + '"><strong>No result.</strong> Please add post to category!</div>';

        }

				$scope.find('.elementor-grid').html(result);
				$scope.find('.elementor-item').removeClass('animate__hide').addClass('animate__show');

				$scope.find('.give-card__progress-custom .give-goal-progress').each( function() {
					if( ! $(this).parent().hasClass('give-card__progress-custom') || ! $(this).find('.give-progress-bar').length ) {
						return;
					}

					getProgressBarFilter( $(this) );

				});

			});
		});

 	};

	function getPieChart( $selector ) {
		//console.log($selector);
		var $innerText = $selector.data('innertext'),
				$strokeWidth = $selector.data('strokewidth'),
				$easing = $selector.data('easing'),
				$duration = $selector.data('duration'),
				$color = $selector.data('color'),
				$trailColor = $selector.data('trailcolor'),
				$trailWidth = $selector.data('trailwidth'),
				$toColor = $selector.data('tocolor');
				$svgWidth = $selector.data('width'),
				$svgHeight = $selector.data('height');

		var bar = new ProgressBar.Circle($selector[0], {
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

		    var value = Math.round(bar.value() * 100);
				if( $innerText ) {
					bar.setText(value + '% <span>' + $innerText + '</span>');
				} else {
					bar.setText(value + '%');
				}

			}
		});

		var $barWidth = $selector.attr('aria-valuenow') / 100,

				waypoint = new Waypoint({
					element: $selector,
					handler: function() {
						bar.animate($barWidth);  // Number from 0.0 to 1.0
					},
					offset: '100%',
					triggerOnce: true
				});
	}

	var PieChartHandler = function( $scope, $ ) {
		//console.log($scope);
		$scope.find('.elementor-pie-chart__progress').each( function() {
			if( ! $(this).length ) {
				return;
			}
			getPieChart( $(this) );

		});

 	};

	function getProgressBar( $selector ) {

		$selector.find('.give-progress-bar').css('display','none');

		var $type = $selector.parent().data('type'),
				$strokeWidth = $selector.parent().data('strokewidth'),
				$easing = $selector.parent().data('easing'),
				$duration = $selector.parent().data('duration'),
				$color = $selector.parent().data('color'),
				$trailColor = $selector.parent().data('trailcolor'),
				$trailWidth = $selector.parent().data('trailwidth'),
				$toColor = $selector.parent().data('tocolor');
				$svgWidth = $selector.parent().data('width'),
				$svgHeight = $selector.parent().data('height');

				if( 'circle' === $type ) {
					var bar = new ProgressBar.Circle($selector[0], {
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
							var value = Math.round(bar.value() * 100) + '%';
					    if (value === 0) {
					      bar.setText('');
					    } else {
					      bar.setText(value);
					    }
						}
					});
				} else {
					var bar = new ProgressBar.Line($selector[0], {
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

				var $barWidth = $selector.find('.give-progress-bar').attr('aria-valuenow') / 100,

						waypoint = new Waypoint({
							element: $selector,
							handler: function() {
								bar.animate($barWidth);  // Number from 0.0 to 1.0
							},
							offset: '100%',
							triggerOnce: true
						});
	}

	function getProgressBarFilter( $selector ) {

		$selector.find('.give-progress-bar').css('display','none');

		var $type = $selector.parent().data('type'),
				$strokeWidth = $selector.parent().data('strokewidth'),
				$easing = $selector.parent().data('easing'),
				$duration = $selector.parent().data('duration'),
				$color = $selector.parent().data('color'),
				$trailColor = $selector.parent().data('trailcolor'),
				$trailWidth = $selector.parent().data('trailwidth'),
				$toColor = $selector.parent().data('tocolor');
				$svgWidth = $selector.parent().data('width'),
				$svgHeight = $selector.parent().data('height');

				if( 'circle' === $type ) {
					var bar = new ProgressBar.Circle($selector[0], {
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
							var value = Math.round(bar.value() * 100) + '%';
					    if (value === 0) {
					      bar.setText('');
					    } else {
					      bar.setText(value);
					    }
						}
					});
				} else {
					var bar = new ProgressBar.Line($selector[0], {
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

				var $barWidth = $selector.find('.give-progress-bar').attr('aria-valuenow') / 100;

				bar.animate($barWidth);  // Number from 0.0 to 1.0
	}

	var ProgressbarHandler = function( $scope, $ ) {
		//console.log($scope);
		$scope.find('.give-card__progress-custom .give-goal-progress').each( function() {
			if( ! $(this).parent().hasClass('give-card__progress-custom') || ! $(this).find('.give-progress-bar').length ) {
				return;
			}

			getProgressBar( $(this) );

		});

 	};

	var SwiperSliderHandler = function( $scope, $ ) {
		//console.log($scope);
		var $selector = $scope.find('.swiper-container'),
				$dataSwiper  = $selector.data('swiper'),
				mySwiper = new Swiper($selector, $dataSwiper);

	};

	var SwiperSliderThumbsHandler = function( $scope, $ ) {
		//console.log($scope);
		var $selector_thumbs = $scope.find('.swiper-thumbs .swiper-container'),
				$dataSwiperThumbs  = $selector_thumbs.data('swiper'),
				thumbSwiper = new Swiper($selector_thumbs, $dataSwiperThumbs);

		var $selector = $scope.find('.swiper-main .swiper-container'),
				$dataSwiper  = $selector.data('swiper');

				$dataSwiper['thumbs'] = { swiper: thumbSwiper, };
		var mainSwiper = new Swiper($selector, $dataSwiper);
	};

	var GivePopupHandler = function( $scope, $ ) {
		//console.log($scope);
		var modal_skin = $scope.find('.elementor-give-modal-wrap').data('skin'),
				form_id = $scope.find('form').attr('id');
				
		$scope.find('button.give-btn-modal').attr('data-mfp-src', '#' + form_id);

		$scope.find('button.give-btn-modal').magnificPopup({
      type: 'inline',
      midClick: true,
      callbacks: {
        beforeOpen: function() {
          // Will fire when this exact popup is opened
					$scope.find('form.give-form').addClass(modal_skin);

					if( $scope.find('.give-form-wrap').hasClass('give-display-button') ) {
						$scope.find('button.give-btn-modal').hide();
					} else {
						$scope.find('div.give-total-wrap').hide();
						$scope.find('#give-donation-level-button-wrap').hide();
						$scope.find('button.give-btn-modal').hide();
					}
        },
        beforeClose: function() {
          // Will fire when popup is closed
					$('.mfp-wrap').find('form.give-form').removeClass(modal_skin);

					if( $scope.find('.give-form-wrap').hasClass('give-display-button') ) {
						$scope.find('button.give-btn-modal').show();
					} else {
						$('.mfp-wrap').find('div.give-total-wrap').show();
						$('.mfp-wrap').find('#give-donation-level-button-wrap').show();
						$('.mfp-wrap').find('button.give-btn-modal').show();
					}
        },
				close: function() {
          // Will fire when popup is closed
					$scope.find('form.give-form').removeClass('mfp-hide');
        }
      }
    });
	};

	// Make sure you run this code under Elementor.
	$( window ).on( 'elementor/frontend/init', function() {

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-counter.default', CounterHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-countdown.default', CountDownHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-pie-chart.default', PieChartHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-video-play-button.default', MagnificPopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-video-box.default', MagnificPopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-video-box.skin-pumori', MagnificPopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-video-box.skin-baruntse', MagnificPopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-video-box.skin-coropuna', MagnificPopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-video-box.skin-cholatse', MagnificPopupHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-base-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-base-carousel.skin-grid-pumori', SwiperSliderHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-logo-carousel.default', SwiperSliderHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-grid-nevado', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-baruntse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-coropuna', SwiperSliderThumbsHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-ampato', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-andrus', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-saltoro', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-changtse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-changla', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-galloway', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-jorasses', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-testimonial-carousel.skin-list-cholatse', SwiperSliderHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members.skin-pumori', FilterPostHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-pumori', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-batura', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-changla', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-havsula', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-taboche', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-cerredo', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-cholatse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-members-carousel.skin-jimara', SwiperSliderHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts.skin-grid-yutmaru', FilterPostHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-pumori', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-baruntse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-coropuna', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-andrus', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-saltoro', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-batura', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-changtse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-taboche', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-castor', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-wilson', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-jorasses', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-michelson', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-cerredo', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-gangri', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-sankar', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-cholatse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-tronador', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-posts-carousel.skin-grid-jimara', SwiperSliderHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-projects-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-projects-carousel.skin-grid-hardeol', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-projects-carousel.skin-grid-galloway', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-projects-carousel.skin-grid-jorasses', SwiperSliderHandler );

		// WooCommerce.
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-products-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-products-carousel.skin-grid-andrus', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-products-carousel.skin-grid-havsula', SwiperSliderHandler );

		// Give.
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-uber-menu.default', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-form-button.default', GivePopupHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.default', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-pumori', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-pumori', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-baruntse', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-baruntse', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-coropuna', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-coropuna', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-saltoro', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-saltoro', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-taboche', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-taboche', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-galloway', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-galloway', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-wilson', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-changla', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-changla', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-jorasses', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-totals.skin-jorasses', GivePopupHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-form.skin-andrus', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-form.skin-tronador', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-form.skin-yutmaru', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-form.skin-vaccine', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-form.skin-jimara', GivePopupHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.default', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-pumori', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-coropuna', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-coropuna', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-list-andrus', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-changtse', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-changtse', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-hardeol', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-hardeol', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-nevado', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-taboche', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-galloway', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-havsula', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-cobble-paradis', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-cobble-castor', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-cholatse', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-tronador', FilterPostHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-tronador', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-vaccine', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-vaccine', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-yutmaru', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms.skin-grid-yutmaru', GivePopupHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.default', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-pumori', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-pumori', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-coropuna', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-coropuna', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-coropuna', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-changtse', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-changtse', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-changtse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-hardeol', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-hardeol', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-hardeol', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-nevado', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-nevado', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-taboche', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-taboche', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-galloway', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-galloway', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-havsula', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-havsula', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-wilson', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-list-saltoro', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-list-saltoro', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-list-saltoro', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-cholatse', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-cholatse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-vaccine', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-vaccine', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-vaccine', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-yutmaru', ProgressbarHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-yutmaru', GivePopupHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-give-forms-carousel.skin-grid-yutmaru', SwiperSliderHandler );

		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-donors-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-donors-carousel.skin-saltoro', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-donors-carousel.skin-taboche', SwiperSliderHandler );

		// Tribe Events.
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events.skin-list-baruntse', FilterPostHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-andrus', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-changla', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-havsula', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-castor', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-grouse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-sankar', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-manaslu', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-events-carousel.skin-grid-yutmaru', SwiperSliderHandler );

		// Sermone
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-sermone-carousel.default', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-sermone-carousel.skin-grid-grouse', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-sermone-carousel.skin-grid-michelson', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-sermone-carousel.skin-grid-gangri', SwiperSliderHandler );
		elementorFrontend.hooks.addAction( 'frontend/element_ready/be-sermone-carousel.skin-grid-sankar', SwiperSliderHandler );

	} );

} )( jQuery );
