P_VARIABLE_API = """; Homing State P Variable
#define HomingState       P1000
#define StateIdle         0
#define StateConfiguring  1
#define StateMoveNeg      2
#define StateMovePos      3
#define StateHoming       4
#define StatePostHomeMove 5
#define StateAligning     6
#define StateDone         7
#define StateFastSearch   8
#define StateFastRetrace  9
#define StatePreHomeMove  10
HomingState = StateIdle

; Homing Status P Variable
#define HomingStatus      P1001
#define StatusDone        0
#define StatusHoming      1
#define StatusAborted     2
#define StatusTimeout     3
#define StatusFFErr       4
#define StatusLimit       5
#define StatusIncomplete  6
#define StatusInvalid     7
#define StatusPaused      8
#define StatusDebugHoming 9
HomingStatus = StatusDone

; Homing Group P Variable
#define HomingGroup       P1002
HomingGroup = 0

; Homing Group Backup P Variable
#define HomingBackupGroup P1003
HomingBackupGroup = 0
"""

CLOSE = """CLOSE"""
