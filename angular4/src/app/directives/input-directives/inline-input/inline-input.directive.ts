import { Component, OnInit, Input, Output, EventEmitter, AfterViewInit, HostListener } from '@angular/core';
import { CurrencyPipe } from 'app/pipes';

@Component({
    selector: '[appInlineInput]',
    templateUrl: './inline-input.directive.html',
    providers: [ CurrencyPipe ]

})
export class InlineInputDirective implements OnInit {
    innerValue: string = '';
    oldValue: string = '';
    @Output() valueChange: EventEmitter<any> = new EventEmitter();
    mode: string = 'display';
    @Input('currency') currencyFormat: string = 'INR';

    constructor() { }

    ngOnInit() { }

    @Input('value')
    set value(val: any) {
        this.innerValue = this.oldValue = val;
    }

    save() {
        this.valueChange.emit(this.innerValue);
        this.mode = 'display';
    }

    cancel() {
        this.innerValue = this.oldValue;
        this.save();
    }

}
