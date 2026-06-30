import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-confirm-dialog',
  imports: [CommonModule, TranslateModule],
  templateUrl: './confirm-dialog.html',
  styleUrl: './confirm-dialog.scss',
})
export class ConfirmDialog {
  @Input() visible = false;
  @Input() titleKey = '';
  @Input() messageKey = '';
  @Input() messageParams: Record<string, string | number> = {};
  @Input() cancelKey = 'COMMON.CONFIRM_NO';
  @Input() confirmKey = 'COMMON.CONFIRM_YES_DELETE';

  @Output() cancelled = new EventEmitter<void>();
  @Output() confirmed = new EventEmitter<void>();

  onBackdropClick(): void {
    this.cancelled.emit();
  }

  onCancel(): void {
    this.cancelled.emit();
  }

  onConfirm(): void {
    this.confirmed.emit();
  }
}
