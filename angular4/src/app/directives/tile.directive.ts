import { Directive, ElementRef } from '@angular/core';
declare var jQuery: any;

@Directive({
    selector: '[appTile]'
})

export class TileDirective {

    $el: any;

    constructor(el: ElementRef) {
        this.$el = jQuery(el.nativeElement);
    }

    ngAfterContentInit(): void {
        this.$el
            .css('height', '104px')
            .css('backgroundColor', this.$el.data('color'))
            .liveTile();
    }

}
