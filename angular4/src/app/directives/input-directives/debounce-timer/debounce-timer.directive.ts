import { Directive, ElementRef, Input, Output, EventEmitter, AfterViewInit } from '@angular/core';
import { Observable } from 'rxjs/Rx';

@Directive({
  selector: '[appDebounceTimer]',
  host: {
    '(change)': 'emitValue($event.target.value)'
  }
})
export class DebounceTimerDirective {
  @Input('appDebounceTimer') debounceTime: number = 400;
  @Output('valueChanged') valueEmitter: EventEmitter<any> = new EventEmitter();

  constructor(private _elementRef: ElementRef) { }

  ngAfterViewInit() {

    // Listener for input keyup event with delay time
    Observable.fromEvent(this._elementRef.nativeElement, 'keyup')
      .debounceTime(this.debounceTime)
      .subscribe((event: any) => {
        this.emitValue(event.target.value)
      });
  }

  // Emit modal value to outside world
  emitValue(value) {
    this.valueEmitter.emit(value);
  }
}