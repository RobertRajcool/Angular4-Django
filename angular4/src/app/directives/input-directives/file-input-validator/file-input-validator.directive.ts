import { Directive, Input, Output, EventEmitter } from "@angular/core";
import { NG_VALUE_ACCESSOR, ControlValueAccessor, Validators, NG_VALIDATORS, FormControl } from "@angular/forms";
import { getControlName } from 'app/directives';
import { MIMI_TYPES } from './file-mime-types';

@Directive({
    selector: "[appValidateFileInput]",
    host: {
        "(change)": "onChange($event.target.files)",
        "(blur)": "onTouched()"
    },
    providers: [
        { provide: NG_VALUE_ACCESSOR, useExisting: FileValueAccessorDirective, multi: true },
        { provide: NG_VALIDATORS, useExisting: FileValueAccessorDirective, multi: true }
    ]
})
export class FileValueAccessorDirective implements ControlValueAccessor, Validators {
    value: any;
    onChange = (_) => { };
    onTouched = () => { };
    @Input('fileRequired') required: boolean = true;
    maxFileSize: number;
    validFileTypes: Array<string>;
    validFileTypeExtensions: Array<string>;
    @Output('fileUrls') fileNames: EventEmitter<Array<string>> = new EventEmitter();

    writeValue(value) { }
    registerOnChange(fn: any) { this.onChange = fn; }
    registerOnTouched(fn: any) { this.onTouched = fn; }

    public validate(c: FormControl): boolean | Object {
        if (this.required && c.value.length <= 0) return { 'fileRequired': `Please select a file for ${getControlName(c)}` };
        else if (this.maxFileSize || this.validFileTypes) return this.validateFiles(c.value);
        else return null;
    }

    validateFiles(files: Array<File>): boolean | Object {
        let fileSrcList: Array<string> = [];
        const reader = new FileReader();

        reader.onload = ((e) => {
            let src = e.target['result']; 
            fileSrcList.push(src);
            if (fileSrcList.length > 0) this.fileNames.emit(fileSrcList);
        });

        if (files && files.length > 0) {
            for (let i = 0; i < files.length; i++) {
                // Validating file size
                if (this.maxFileSize && (files[i].size / 1000) > this.maxFileSize) {
                    return { 'tooLargeFile': `Selected file is too large. Select below ${this.maxFileSize} kb.` };
                }
                // Validating file type
                else if (this.validFileTypes && this.validFileTypes.indexOf(files[i].type) < 0) {
                    return { 'invalidFileType': `Selected file is not valid. Valid file types are ${this.validFileTypeExtensions.join(', ')}.` };
                }
                // Gathering urls
                else {
                    reader.readAsDataURL(files[0]);
                }
            }
        }
        
        return null;
    }

    @Input('maxSize') set MaximumFileSize(size: any) {
        this.maxFileSize = parseFloat(size);
    }

    @Input('validTypes') set fileTypes(types: Array<string>) {

        if (types instanceof Array && types.length > 0) {
            this.validFileTypeExtensions = [];
            this.validFileTypes = [];

            types.forEach(fType => {
                this.validFileTypeExtensions.push(fType);
                this.validFileTypes.push(MIMI_TYPES[fType]);
            });
        } else {
            this.validFileTypes = undefined;
            this.validFileTypeExtensions = undefined;
        }
    }
}
