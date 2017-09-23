import { Component, OnInit, ViewEncapsulation, Input, Output, AfterViewInit, HostListener, Renderer, ElementRef, forwardRef, OnDestroy } from '@angular/core';
import { FormControl, NG_VALUE_ACCESSOR, ControlValueAccessor, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Subscription } from 'rxjs/Subscription';
import { AipDirectoryService } from 'app/services';
import { ValidationService } from 'app/directives';
import { EmailRecepients } from 'app/classes';

@Component({
    selector: 'app-mail-recipient-collector',
    encapsulation: ViewEncapsulation.Emulated,
    templateUrl: './mail-recipient-collector.directive.html',
    styleUrls: ['./mail-recipient-collector.directive.scss'],
    providers: [
        {
            provide: NG_VALUE_ACCESSOR,
            useExisting: forwardRef(() => MailRecipientCollectorDirective),
            multi: true
        }
    ]
})
export class MailRecipientCollectorDirective implements OnInit, ControlValueAccessor {
    innerValue: Array<EmailRecepients>;
    private onTouchedCallback: () => void = () => { };
    private onChangeCallback: (_: any) => void = () => { };
    @Input() placeholder: string;
    collectForm: FormGroup;
    enableCollector: boolean = false;
    unregister: Function;

    constructor(
        private el_ref: ElementRef,
        private renderer: Renderer,
        private fb: FormBuilder
    ) {
        this.collectForm = this.fb.group({
            'name': ['', [Validators.required]],
            'email': ['', [Validators.required, ValidationService.emailValidator]]
        })
    }

    ngOnInit() {
        // Listener for focusing search input
        this.el_ref.nativeElement.addEventListener("DOMNodeInserted", Event => {
            let el: HTMLElement = Event.target;
            if (el.classList.contains('collect-form-group')) {
                el.getElementsByTagName('input')[0].focus();
            }
        }, false);
    }
    // Set Touched on blur
    onBlur() {
        this.onTouchedCallback();
    }

    // From ControlValueAccessor Interface
    writeValue(value: any) {
        if (value !== this.innerValue) {
           this.innerValue = value;
        }
    }

    // From ControlValueAccessor Interface
    registerOnChange(fn: any) {
        this.onChangeCallback = fn;
    }

    // From ControlValueAccessor Interface
    registerOnTouched(fn: any) {
        this.onTouchedCallback = fn;
    }

    // Add or Remove Listener for window click & Toggle select dropdown
    @HostListener('click', ['$event']) onComponentClick(event: MouseEvent) {

        if (!this.enableCollector) {
            this.unregister = this.renderer.listenGlobal('document', 'click', Event => {
                if (!this.el_ref.nativeElement.contains(Event.target)) {
                    this.collectForm.reset();
                    this.enableCollector = false;
                    this.unregister();
                } else {
                    this.enableCollector = true;
                }
            });
        }
    }

    // Remove item from list
    popItem(index: number) {
        let poped = this.innerValue.splice(index, 1);

    }

    // Update form value
    updateValue(value: any) {
        if (this.innerValue !== value) {
            this.innerValue = value;
            this.onChangeCallback(this.innerValue);
        }
    }

    onKeyPress(event: KeyboardEvent, focus_el: HTMLElement) {
        // On Enter submit form
        if (event.keyCode == 13) {
            if (this.collectForm.valid) {
                let newValue = this.innerValue;
                if(!(newValue instanceof Array)) newValue = [];
                
                newValue.push({ name: this.collectForm.value['name'], 'email': this.collectForm.value['email'] });
                this.updateValue(newValue);
                this.collectForm.reset();
                focus_el.focus();

                for (var ctrl_name of Object.keys(this.collectForm.controls)) {
                    this.collectForm.controls[ctrl_name].markAsUntouched();
                }
            }
            else {
                for (var ctrl_name of Object.keys(this.collectForm.controls)) {
                    this.collectForm.controls[ctrl_name].markAsTouched();
                }
            }
        }
    }

    // Get error messages
    get errorMessage() {

        var errors: Array<any> = [];

        for (var ctrl_name of Object.keys(this.collectForm.controls)) {
            var control: any = this.collectForm.controls[ctrl_name];
            for (let propertyName in control.errors) {
                if (control.errors.hasOwnProperty(propertyName) && control.touched) {
                    errors.push(`${ctrl_name}: ${ValidationService.getValidatorErrorMessage(propertyName, control.errors[propertyName], ctrl_name)}`);
                }
            }
        }

        return errors;
    }

}
