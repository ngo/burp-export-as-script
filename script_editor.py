from javax.swing import JFrame, JPanel, JSplitPane, JTable, JEditorPane, GroupLayout, JButton, JScrollPane, JFileChooser
from javax.swing.table import AbstractTableModel
from java.awt import Dimension

from collections import namedtuple

HttpMessage = namedtuple("HttpMessage", [
        'http_service', 
        'req_data',
        'resp_data',
        'req_info',
        'resp_info'
])

from script_generator import generate_script


#Message is a tuple: req, req_info, resp, resp_info, comment

class ReqListDataModel(AbstractTableModel):
    column_names = [
        "#",
        "Method",
        "URL",
        "Status",
        "Length"
    ]

    def __init__(self, messages):
        self._messages = messages

    def getRowCount(self):
        return len(self._messages)

    def getColumnCount(self):
        return len(ReqListDataModel.column_names)

    def getColumnName(self, column):
        return self.column_names[column]

    def getValueAt(self, row, column):
        col_name = self.column_names[column]
        if col_name == "#":
            return row
        if col_name == "Method":
            return self._messages[row].req_info.getMethod()
        if col_name == "URL":
            return self._messages[row].req_info.getUrl()
        if col_name == "Status":
            return self._messages[row].resp_info.getStatusCode()
        if col_name == "Length":
            return len(self._messages[row].resp_data)

class ScriptEditor(object):

    def __init__(self, messages):
        self._messages = messages
        frame = JFrame("Export to script")
        mainPanel = JPanel()
        frame.add(mainPanel)
        
        button_pane = JPanel()
        options_button = JButton("Options")
        regen_button = JButton("Regenerate", actionPerformed=self.gen_script)
        save_button = JButton("Save", actionPerformed=self.save)
        close_button = JButton("Close", actionPerformed=lambda evt: frame.dispose())

        button_pane.add(options_button)
        button_pane.add(regen_button)
        button_pane.add(save_button)
        button_pane.add(close_button)
        button_pane.setMaximumSize(Dimension(
            1000000,
            40
        ) );

        reqtab = JTable(ReqListDataModel(self._messages))
        self._editor = JEditorPane()
        reqtab_editor = JSplitPane(
                JSplitPane.VERTICAL_SPLIT,
                JScrollPane(reqtab),
                JScrollPane(self._editor)
        )

        layout = GroupLayout(mainPanel)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        mainPanel.setLayout(layout)

        layout.setVerticalGroup(
            layout.createSequentialGroup().addComponent(reqtab_editor).addComponent(button_pane)
        )
        layout.setHorizontalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                    .addComponent(reqtab_editor).addComponent(button_pane)
                )
        )
        self.gen_script()
        frame.setVisible(True)

    def gen_script(self, _=None):
        script = generate_script(self._messages)
        self._editor.setText(script)

    def save(self, _):
        chooser = JFileChooser()
        if chooser.showSaveDialog(None) == JFileChooser.APPROVE_OPTION:
            with open(chooser.getSelectedFile().getAbsolutePath(), 'w') as f:
                f.write(self._editor.getText())

if __name__ == "__main__":
    ScriptEditor([])
