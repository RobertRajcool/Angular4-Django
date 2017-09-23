import { Directive, HostListener, ElementRef, OnInit, Input } from '@angular/core';
import { CurrencyPipe } from 'app/pipes';

@Directive({
    selector: '[appCurrencyFormatter]'
})
export class CurrencyFormatterDirective {
    element: HTMLInputElement;
    @Input('fraction') decimalFractions: number = 2;
    @Input('currency') currencyFormat: string = 'INR';

    constructor(
        private el_ref: ElementRef,
        private currencyPipe: CurrencyPipe
    ) {
        this.element = this.el_ref.nativeElement
    }

    ngOnInit() {
        if (this.element.value)
            this.element.value = this.currencyPipe.transform(this.element.value, this.decimalFractions, this.currencyFormat);
    }

    @Input('ngModel')
    set ElementValue(value: any) {
        if (document.activeElement != this.element)
            setTimeout(() => { this.element.value = this.currencyPipe.transform(value, this.decimalFractions, this.currencyFormat); }, 1);
    }

    // Parse into decimal on focus
    @HostListener("focus", ["$event.target.value"])
    onFocus(value) {
        this.element.value = this.currencyPipe.parse(value, this.decimalFractions); // opossite of transform
    }

    // Transform into currency format on blur
    @HostListener("blur", ["$event.target.value"])
    onBlur(value) {
        if (value) this.element.value = this.currencyPipe.transform(value, this.decimalFractions, this.currencyFormat);
        else this.element.value = '';
    }

    // Validating typing 
    @HostListener("keypress", ["$event"])
    validate(event) {

        var theEvent = event || window.event;
        var keyCode = theEvent.keyCode || theEvent.which;
        var key = String.fromCharCode(keyCode);
        let regex = new RegExp("[0-9.]");
        //let regex = new RegExp(" /[0-9]+/");
        let dot_position = this.element.value.indexOf(".");

        /* if (keyCode < 46 || event.key == "Delete") {
            theEvent.returnValue = true;
        } */
        if ((47 < keyCode) && (keyCode < 58) || keyCode == 8 || keyCode == 189 || keyCode == 109 || event.key == "Delete") {
               theEvent.returnValue = true;
          }
        else if (
            !regex.test(key) ||
            (key == "." && dot_position >= 0) ||
            (dot_position >= 0 && this.element.value.slice(dot_position + 1).length >= this.decimalFractions)
        ) {
            theEvent.returnValue = false;
            if (theEvent.preventDefault) theEvent.preventDefault();
        }
    }

}
