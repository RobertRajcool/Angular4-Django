import { Component, OnInit, ViewEncapsulation, Input, Output, AfterViewInit, HostListener, Renderer, ElementRef, forwardRef } from '@angular/core';
import { FormControl, NG_VALUE_ACCESSOR, ControlValueAccessor } from '@angular/forms';
import { Subscription } from 'rxjs/Subscription';
import { AipDirectoryService } from 'app/services';
import 'rxjs/add/operator/debounceTime';


// Styles..........................................
const styles = `.display {
    cursor: pointer;
}
.display .form-control:disabled {
    cursor: pointer;
    background: #fff;
}
.display .form-control[readonly] {
    background: transparent;
}
.search .dropdown-menu {
    position: relative;
    min-width: 100%;
    display: block;
    max-height: 250px;
    overflow-y: scroll;
    top: -4px;
}
.search .dropdown-item:hover, .search .dropdown-menu li:focus {
    background-color: #428bca;
    color: #fff;
    border: none;
    outline: none;
}
.disabled {
    cursor: not-allowed !important;
}
.disabled .form-control, .disabled .form-control:disabled, .disabled .input-group-addon {
    cursor: not-allowed !important;
    background: #eeeeee !important;
    opacity: 1;
}`

// Component ......................................
@Component({
    selector: 'app-locality-select',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './locality-select.directive.html',
    styles: [styles],
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => LocalitySelectDirective),
            multi: true
        },
    ]
})
export class LocalitySelectDirective implements OnInit, ControlValueAccessor {
    private innerValue: string = '';
    private onTouchedCallback: () => void = () => { };
    private onChangeCallback: (_: any) => void = () => { };
    @Input('property') locality_property: string = 'district';
    @Input('relDisCtrl') district_input_ctrl: FormControl;
    @Input('relStateCtrl') state_input_ctrl: FormControl;
    select: boolean = false;
    search: boolean = false;
    typo: FormControl = new FormControl();
    unregister: Function;
    disabled: boolean = false;
    list: Array<{
        id: number;
        pincode?: string;
        district: string;
        state: string;
    }> = [];
    focusedOption: number;
    foucusingUnregister: Function;

    constructor(
        private renderer: Renderer,
        private el_ref: ElementRef,
        private aipdService: AipDirectoryService
    ) { }


    ngOnInit() {
        // Listener for focusing search input
        this.el_ref.nativeElement.addEventListener("DOMNodeInserted", Event => {
            let el = Event.target;
            if (el.classList.contains('search')) {
                el.getElementsByTagName('input')[0].focus();
            }
        }, false);

        // Listener for gathering list from server on search text changes
        this.typo.valueChanges
            .debounceTime(500)
            .subscribe(
            search_text => {
                if (search_text) {
                    this.search = true;
                    this.gatherList(search_text);
                }
            });
    }

    // Add or Remove Listener for window click & Toggle select dropdown
    @HostListener('focusin', ['$event']) onComponentFocusIn(event: FocusEvent) {

        if (!this.select && !this.disabled) {
            this.unregister = this.renderer.listenGlobal('document', 'click', Event => {
                if (!this.el_ref.nativeElement.contains(Event.target)) {
                    this.select = false;
                    this.unregister();
                    if (this.foucusingUnregister) this.foucusingUnregister();
                }
            });

            this.foucusingUnregister = this.renderer.listenGlobal('document', 'focusin', Event => {
                if (!this.el_ref.nativeElement.contains(Event.target)) {
                    this.select = false;
                    this.foucusingUnregister();
                } else {
                    this.select = true;
                }

                Event.preventDefault();
            });
        }
    }


    // Keyboard events
    @HostListener('keydown', ['$event']) onKeyDown(event: KeyboardEvent) {

        // Arrow keys
        if ([9, 37, 38, 39, 40].indexOf(event.keyCode) >= 0 && this.select) {
            let listOptions: Array<HTMLLIElement> = this.el_ref.nativeElement.querySelectorAll('#dropdown-menu li');

            if (listOptions.length > 0) {
                if (this.focusedOption == undefined || event.target instanceof HTMLInputElement) {
                    this.focusedOption = 0;
                    listOptions[this.focusedOption].focus();
                    event.preventDefault();
                    return;
                }

                // Navigating up
                if (event.keyCode == 37 || event.keyCode == 38 || (event.keyCode == 9 && event.shiftKey)) {
                    if (this.focusedOption - 1 < 0) {
                        if (event.keyCode == 9) return true;
                        else this.focusedOption = listOptions.length - 1;
                    }
                    else this.focusedOption -= 1;

                    listOptions[this.focusedOption].focus();
                    event.preventDefault();
                }

                // Navigating down
                if (event.keyCode == 39 || event.keyCode == 40 || (event.keyCode == 9 && !event.shiftKey)) {
                    if (this.focusedOption + 1 == listOptions.length) {
                        if (event.keyCode == 9) return true;
                        else this.focusedOption = 0;
                    }
                    else this.focusedOption += 1;

                    listOptions[this.focusedOption].focus();
                    event.preventDefault();
                }
            }
        }
        // Enter key ... Selecting option
        else if (event.keyCode == 13 && this.select && event.target instanceof HTMLLIElement) {
            this.selectOpt(this.focusedOption);
        }
    }

    clearOptionFocus() {
        this.focusedOption = undefined;
    }

    // Select option & assign values in to form controls
    selectOpt(index: number, unregisterListener?: boolean) {
        let value: string;
        if (this.locality_property == 'pincode') {
            value = this.list[index].pincode;
            this.setRelDistrict(index);
            this.setRelState(index);
        }
        else if (this.locality_property == 'district') {
            value = this.list[index].district;
            this.setRelState(index);
        }
        else if (this.locality_property == 'state') {
            value = this.list[index].state;
        }

        this.innerValue = this.list[index][this.locality_property];
        this.onChangeCallback(this.list[index][this.locality_property])
        this.select = false;
        this.clearOptionFocus();
        if (this.unregister) this.unregister();
        if (this.foucusingUnregister) this.foucusingUnregister();
        this.typo.reset();

    }

    // Gather list from server
    gatherList(typo: string) {
        this.aipdService.filterAip(this.locality_property, typo)
            .subscribe(
            List => {
                this.list = List;
                this.search = false;
            },
            Error => console.log(Error)
            );
    }

    // Set district if district control exists
    setRelDistrict(index: number) {
        if (this.district_input_ctrl) {
            if (index >= 0) this.district_input_ctrl.setValue(this.list[index]['district']);
            else this.district_input_ctrl.setValue(null);
            this.district_input_ctrl.updateValueAndValidity();
        }
    }
    // Set state if state control exists
    setRelState(index: number) {
        if (this.state_input_ctrl) {
            if (index >= 0) this.state_input_ctrl.setValue(this.list[index].state);
            else this.state_input_ctrl.setValue(null);
            this.state_input_ctrl.updateValueAndValidity();
        }
    }

    // Reset
    resetInnerValue() {
        this.innerValue = '';
        this.setRelDistrict(-1);
        this.setRelState(-1);
        this.onChangeCallback('');
    }

    // Model get function
    get value() {
        return this.innerValue;
    }

    // Model set function
    set value(val: string) {
        if (this.innerValue !== val) {
            this.innerValue = val;
            this.onChangeCallback(val);
        }
    }

    // Set touched on blur
    onBlur() {
        this.onTouchedCallback();
    }

    //From ControlValueAccessor interface
    writeValue(value: string) {
        if (value !== this.innerValue) {
            this.innerValue = value;
        }
    }

    //From ControlValueAccessor interface
    registerOnChange(fn: any) {
        this.onChangeCallback = fn;
    }

    //From ControlValueAccessor interface
    registerOnTouched(fn: any) {
        this.onTouchedCallback = fn;
    }

    //From ControlValueAccessor interface
    setDisabledState(isDisabled: boolean) {
        this.disabled = isDisabled;
    }

    //From Template controls
    @Input('readonly')
    set setAsReadonly(isReadonly: boolean) {
        this.disabled = isReadonly;
    }
}


