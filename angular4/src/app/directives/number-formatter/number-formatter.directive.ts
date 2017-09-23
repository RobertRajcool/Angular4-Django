import { Directive, HostListener, ElementRef, OnInit, Input } from '@angular/core';

@Directive({
  selector: '[appNumberFormatter]'
})
export class NumberFormatterDirective {
    element: HTMLInputElement;
    @Input('fraction') decimalFractions: number = 2;
    @Input('min') minValue: number = 0;

    constructor(
        private el_ref: ElementRef
    ) {
        this.element = this.el_ref.nativeElement
    }

    ngOnInit() {
    }

    // Validating typing 
    @HostListener("keypress", ["$event"])
    validate(event) {

        var theEvent = event || window.event;
        var keyCode = theEvent.keyCode || theEvent.which;
        var key = String.fromCharCode(keyCode);
        let regex;

        if(this.decimalFractions > 0){
            regex = new RegExp("[0-9.]");
        } else {
            regex = new RegExp("[0-9]");
        }

        let dot_position = this.element.value.indexOf(".");
        
        if ((keyCode < 46 && regex.test(key)) || event.key == "Delete") {
            theEvent.returnValue = true;
        }
        else if (
            !regex.test(key) ||
            (key == "." && dot_position >= 0) ||
            (dot_position >= 0 && this.element.value.slice(dot_position + 1).length >= 2) ||
            event.target.value < this.minValue
        ) {
            theEvent.returnValue = false;
            if (theEvent.preventDefault) theEvent.preventDefault();
        }
    }

}
