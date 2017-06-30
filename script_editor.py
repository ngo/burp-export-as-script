from javax.swing import ( 
        JFrame, JPanel, JSplitPane, JTable, JEditorPane, 
        GroupLayout, JButton, JScrollPane, JFileChooser,
        JToggleButton, JCheckBox, BorderFactory
)
from javax.swing.table import AbstractTableModel
from java.awt import Dimension, GridLayout

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
        regen_button = JButton("Regenerate", actionPerformed=self.gen_script)
        save_button = JButton("Save", actionPerformed=self.save)
        close_button = JButton("Close", actionPerformed=lambda evt: frame.dispose())

        self._proxy_checkbox = JCheckBox("Enable proxy through burp")
        self._no_ssl_checkbox = JCheckBox("Disable ssl verification")
        self._debug_checkbox = JCheckBox("Debugging output")
        self._auto_cookie_checkbox = JCheckBox("Allow automatic cookie handling")
        self._debug_checkbox.setSelected(True)
        self._no_ssl_checkbox.setSelected(True)
        checkbox_pane = JPanel()
        checkbox_pane.setBorder(BorderFactory.createTitledBorder("Options"))
        checkbox_pane.setLayout(GridLayout(4,3))

        checkbox_pane.add(self._proxy_checkbox)
        checkbox_pane.add(self._no_ssl_checkbox)
        checkbox_pane.add(self._debug_checkbox)
        checkbox_pane.add(self._auto_cookie_checkbox)
        
        button_pane.add(regen_button)
        button_pane.add(save_button)
        button_pane.add(close_button)
        button_pane.setMaximumSize(Dimension(
            1000000,
            40
        ) );

        reqtab = JTable(ReqListDataModel(self._messages))
        reqtab.setAutoResizeMode(JTable.AUTO_RESIZE_LAST_COLUMN)
        reqtab.getColumnModel().getColumn(0).setPreferredWidth(40)
        reqtab.getColumnModel().getColumn(1).setPreferredWidth(100)
        reqtab.getColumnModel().getColumn(2).setMinWidth(600)
        reqtab.getColumnModel().getColumn(3).setPreferredWidth(100)
        reqtab.getColumnModel().getColumn(4).setPreferredWidth(100)
        self._editor = JEditorPane()
        upper = JScrollPane(reqtab)
        lower = JScrollPane(self._editor)
        reqtab_editor = JSplitPane(
                JSplitPane.VERTICAL_SPLIT,
                upper,
                lower
        )
        layout = GroupLayout(mainPanel)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)
        mainPanel.setLayout(layout)

        layout.setVerticalGroup(
            layout.createSequentialGroup().addComponent(reqtab_editor).addComponent(checkbox_pane).addComponent(button_pane)
        )
        layout.setHorizontalGroup(
            layout.createSequentialGroup()
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                    .addComponent(reqtab_editor).addComponent(checkbox_pane).addComponent(button_pane)
                )
        )
        self.gen_script()
        frame.setVisible(True)
        reqtab_editor.setDividerLocation(150)

    def gen_script(self, _=None):
        proxy_url = None
        if self._proxy_checkbox.isSelected():
            proxy_url = 'http://localhost:8080'
        loglevel = "INFO"
        if self._debug_checkbox.isSelected():
            loglevel = "DEBUG"
        script = generate_script(
            self._messages,
            disable_ssl_verification=self._no_ssl_checkbox.isSelected(),
            proxy=proxy_url,
            loglevel=loglevel,
            auto_cookie=self._auto_cookie_checkbox.isSelected()
        )
        self._editor.setText(script)

    def save(self, _):
        chooser = JFileChooser()
        if chooser.showSaveDialog(None) == JFileChooser.APPROVE_OPTION:
            with open(chooser.getSelectedFile().getAbsolutePath(), 'w') as f:
                f.write(self._editor.getText())

if __name__ == "__main__":
    ScriptEditor([])
