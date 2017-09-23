import { Directive, ElementRef, ViewEncapsulation, OnDestroy } from '@angular/core';
declare var jQuery: any;

@Directive({
    selector: '[ResponsiveSildeLoginDesigner]',
    host: {
        
    }
})

export class ResponsiveSlideLoginDesigner {
    $el: any;

    constructor(el: ElementRef) {
        this.$el = jQuery(el.nativeElement);
    }

    ngAfterContentInit(): void {
       // Slideshow 1
      jQuery("#slider1").responsiveSlides({
        maxwidth: 800,
        speed: 800
      });

      // Slideshow 2
      jQuery("#slider2").responsiveSlides({
        maxwidth: 400,
        speed: 800
      });
	   // Slideshow 2
      jQuery("#slider3").responsiveSlides({
        maxwidth: 400,
        speed: 800
      });
    }
}
