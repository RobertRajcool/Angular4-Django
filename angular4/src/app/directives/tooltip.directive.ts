import { Directive, ElementRef, AfterViewInit, OnDestroy, Input } from '@angular/core';
declare var jQuery: any;

@Directive({
  selector: '[appTooltip]'
})
export class TooltipDirective {
    element: HTMLElement;

  constructor(el_ref: ElementRef) {
      this.element = el_ref.nativeElement;
   }

  ngAfterViewInit() {
      jQuery(this.element).tooltip({ trigger: "hover" });
  }

  // Disabling  tooltip conditionally
  @Input("disableTootip")
  disable(value: boolean){

  }

  ngOnDestroy(){
      jQuery(this.element).tooltip('hide');
  }
}
