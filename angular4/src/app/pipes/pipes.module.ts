import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
    CapitalizePipe,
    InStringPipe,
    InCommaSeperatedPipe,
    TimelineDateTimePipe,
    FormatDateTimePipe,
    CurrencyPipe,
    UnderscoreToSpacePipe,
    InArrayPipe,
    KeysPipe,
    SafePipe,
    RoundPipe,
    TitleCasePipe,
    RowPipe,
    SafeHTMLPipe,
    TruncatePipe
} from './pipes';

@NgModule({
    imports: [CommonModule],
    declarations: [
        CapitalizePipe,
        InStringPipe,
        InCommaSeperatedPipe,
        TimelineDateTimePipe,
        FormatDateTimePipe,
        CurrencyPipe,
        UnderscoreToSpacePipe,
        InArrayPipe,
        KeysPipe,
        SafePipe, 
        RoundPipe,
        TitleCasePipe,
        RowPipe,
        SafeHTMLPipe,
        TruncatePipe
    ],
    exports: [
        CapitalizePipe,
        InStringPipe,
        InCommaSeperatedPipe,
        TimelineDateTimePipe,
        FormatDateTimePipe,
        CurrencyPipe,
        UnderscoreToSpacePipe,
        InArrayPipe,
        KeysPipe,
        SafePipe,
        RoundPipe,
        TitleCasePipe,
        RowPipe,
        SafeHTMLPipe,
        TruncatePipe
    ]
})
export class PipesModule { }
