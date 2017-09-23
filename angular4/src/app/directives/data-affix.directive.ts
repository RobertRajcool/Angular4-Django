import { Directive, Input, ElementRef, HostListener, Injectable } from '@angular/core';

function _window(): any {
    // return the native window obj
    return window;
}

@Injectable()
export class WindowRef {

    get nativeWindow(): any {
        return _window();
    }

}

// Affix directive
@Directive({
    selector: '[app-data-affix]',
    providers: [ WindowRef ]
})

export class DataAffixDirective {
    private _minY: number = 100;
    private _className: string = 'affix';

    @Input('affixMin') set affixMin(minY: number) {
        this._minY = minY || this._minY;
    }

    @Input('affixClass') set affixClass(className: string) {
        this._className = className || this._className;
    }

    constructor(private _element: ElementRef, private _window: WindowRef) {

    }

    @HostListener('window:scroll', ['$event'])
    handleScrollEvent(e) {

        if (this._window.nativeWindow.pageYOffset > this._minY) {

            this._element.nativeElement.classList.add(this._className);

        } else {

            this._element.nativeElement.classList.remove(this._className);
        }
    }
}